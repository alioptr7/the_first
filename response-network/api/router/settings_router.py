from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from response_network.api.auth.dependencies import get_current_active_user, get_current_admin_user
from response_network.api.core.dependencies import get_db as get_db_session
from response_network.api.models.settings import Settings, UserSettings
from response_network.api.models.user import User
from response_network.api.schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingRead,
    UserSettingCreate,
    UserSettingUpdate,
    UserSettingRead
)
from workers.tasks.settings_exporter import export_settings_to_request_network

router = APIRouter(prefix="/settings", tags=["settings"])


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
    
    # Trigger settings export task
    export_settings_to_request_network.delay()
    
    return db_setting


@router.get("/", response_model=List[SettingRead])
async def list_settings(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    is_public: Optional[bool] = None
):
    """List system settings"""
    query = select(Settings)
    
    # If not admin and is_public not specified, only show public settings
    if not current_user.is_admin and is_public is None:
        query = query.where(Settings.is_public == True)
    elif is_public is not None:
        query = query.where(Settings.is_public == is_public)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{key}", response_model=SettingRead)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific system setting"""
    result = await db.execute(select(Settings).where(Settings.key == key))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    # Check access
    if not current_user.is_admin and not setting.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this setting"
        )
    
    return setting


@router.patch("/{key}", response_model=SettingRead, dependencies=[Depends(get_current_admin_user)])
async def update_setting(
    key: str,
    setting: SettingUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a system setting (Admin only)"""
    result = await db.execute(select(Settings).where(Settings.key == key))
    db_setting = result.scalar_one_or_none()
    
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    # Update fields
    for field, value in setting.model_dump(exclude_unset=True).items():
        setattr(db_setting, field, value)
    
    await db.commit()
    await db.refresh(db_setting)
    
    # Trigger settings export task
    export_settings_to_request_network.delay()
    
    return db_setting


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a system setting (Admin only)"""
    result = await db.execute(select(Settings).where(Settings.key == key))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    await db.delete(setting)
    await db.commit()
    
    # Trigger settings export task
    export_settings_to_request_network.delay()


# User Settings Endpoints
@router.post("/user", response_model=UserSettingRead)
async def create_user_setting(
    setting: UserSettingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new user setting"""
    # Check if setting already exists for user
    result = await db.execute(
        select(UserSettings).where(
            UserSettings.user_id == current_user.id,
            UserSettings.key == setting.key
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting '{setting.key}' already exists for this user"
        )
    
    db_setting = UserSettings(
        user_id=current_user.id,
        key=setting.key,
        value=setting.value
    )
    db.add(db_setting)
    await db.commit()
    await db.refresh(db_setting)
    return db_setting


@router.get("/user", response_model=List[UserSettingRead])
async def list_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List settings for the current user"""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/user/{key}", response_model=UserSettingRead)
async def get_user_setting(
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific user setting"""
    result = await db.execute(
        select(UserSettings).where(
            UserSettings.user_id == current_user.id,
            UserSettings.key == key
        )
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    return setting


@router.patch("/user/{key}", response_model=UserSettingRead)
async def update_user_setting(
    key: str,
    setting: UserSettingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a user setting"""
    result = await db.execute(
        select(UserSettings).where(
            UserSettings.user_id == current_user.id,
            UserSettings.key == key
        )
    )
    db_setting = result.scalar_one_or_none()
    
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    # Update value
    db_setting.value = setting.value
    await db.commit()
    await db.refresh(db_setting)
    return db_setting


@router.delete("/user/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_setting(
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a user setting"""
    result = await db.execute(
        select(UserSettings).where(
            UserSettings.user_id == current_user.id,
            UserSettings.key == key
        )
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{key}' not found"
        )
    
    await db.delete(setting)
    await db.commit()