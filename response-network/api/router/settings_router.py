from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.dependencies import get_current_active_user, get_current_admin_user
from db.session import get_db_session
from models.settings import Settings, UserSettings
from models.user import User
from schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingRead,
    UserSettingCreate,
    UserSettingUpdate,
    UserSettingRead
)
from workers.tasks.settings_exporter import export_settings_to_request_network

router = APIRouter(prefix="/settings", tags=["Settings"])

# System Settings Endpoints (Admin Only)
@router.post("/", response_model=SettingRead, dependencies=[Depends(get_current_admin_user)])
async def create_setting(
    setting: SettingCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new system setting (Admin only)"""
    # Check if setting with same key exists
    existing = await db.execute(select(Settings).where(Settings.key == setting.key))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting.key}' already exists"
        )

    db_setting = Settings(**setting.model_dump())
    db.add(db_setting)
    await db.commit()
    await db.refresh(db_setting)
    return db_setting

@router.get("/", response_model=List[SettingRead])
async def list_settings(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    user_specific: Optional[bool] = None
):
    """List all settings (filtered by user_specific if specified)"""
    query = select(Settings)
    if user_specific is not None:
        query = query.where(Settings.is_user_specific == user_specific)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{setting_id}", response_model=SettingRead)
async def get_setting(
    setting_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific setting"""
    setting = await db.get(Settings, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/{setting_id}", response_model=SettingRead, dependencies=[Depends(get_current_admin_user)])
async def update_setting(
    setting_id: UUID,
    setting_update: SettingUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a system setting (Admin only)"""
    db_setting = await db.get(Settings, setting_id)
    if not db_setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    for field, value in setting_update.model_dump(exclude_unset=True).items():
        setattr(db_setting, field, value)
    
    db_setting.is_synced = False
    await db.commit()
    await db.refresh(db_setting)
    return db_setting

# User Settings Endpoints
@router.post("/user", response_model=UserSettingRead)
async def create_user_setting(
    user_setting: UserSettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Create or update a user-specific setting"""
    # Check if setting exists and is user-specific
    setting = await db.get(Settings, user_setting.setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    if not setting.is_user_specific:
        raise HTTPException(
            status_code=400,
            detail="This setting does not support user-specific values"
        )

    # Check if user setting already exists
    query = select(UserSettings).where(
        UserSettings.user_id == current_user.id,
        UserSettings.setting_id == user_setting.setting_id
    )
    existing = await db.execute(query)
    db_user_setting = existing.scalar_one_or_none()

    if db_user_setting:
        # Update existing
        db_user_setting.value = user_setting.value
        db_user_setting.is_synced = False
    else:
        # Create new
        db_user_setting = UserSettings(
            user_id=current_user.id,
            setting_id=user_setting.setting_id,
            value=user_setting.value,
        )
        db.add(db_user_setting)

    await db.commit()
    await db.refresh(db_user_setting)
    return db_user_setting

@router.get("/user", response_model=List[UserSettingRead])
async def list_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all settings for the current user"""
    query = select(UserSettings).where(UserSettings.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/user/{setting_id}", response_model=UserSettingRead)
async def update_user_setting(
    setting_id: UUID,
    setting_update: UserSettingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update a user-specific setting"""
    query = select(UserSettings).where(
        UserSettings.user_id == current_user.id,
        UserSettings.setting_id == setting_id
    )
    result = await db.execute(query)
    db_user_setting = result.scalar_one_or_none()

    if not db_user_setting:
        raise HTTPException(status_code=404, detail="User setting not found")

    db_user_setting.value = setting_update.value
    db_user_setting.is_synced = False
    
    await db.commit()
    await db.refresh(db_user_setting)
    return db_user_setting


@router.post("/export", status_code=202)
async def trigger_settings_export(
    db: AsyncSession = Depends(get_db_session),
    _: dict = Depends(get_current_admin_user)
):
    """صادرات دستی تنظیمات به شبکه درخواست"""
    try:
        # فراخوانی تسک Celery با force_export=True
        task = export_settings_to_request_network.delay(force_export=True)
        return {"message": "درخواست صادرات تنظیمات با موفقیت ثبت شد.", "task_id": task.id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در شروع فرآیند صادرات تنظیمات: {str(e)}"
        )