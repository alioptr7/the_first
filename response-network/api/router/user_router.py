from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from core.dependencies import get_db
from models.schemas import UserCreate, UserUpdate, User, UserWithStats
from models.user import User as UserModel
from auth.dependencies import get_current_admin_user
from crud import users as user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserWithStats])
async def list_users(
    profile_type: Optional[str] = Query(None, enum=['admin', 'user', 'viewer']),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get list of users with their request statistics.
    Only admins can access this endpoint.
    """
    return await user_service.get_users_with_stats(
        db,
        profile_type=profile_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

@router.get("/{user_id}", response_model=UserWithStats)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get detailed information about a specific user including their request statistics.
    Only admins can access this endpoint.
    """
    user = await user_service.get_user_with_stats(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Create a new user.
    Only admins can create new users.
    """
    return await user_service.create_user(db, user_in)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Update user information.
    Only admins can update users.
    """
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_service.update_user(db, user, user_in)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Delete a user.
    Only admins can delete users.
    """
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Suspend a user's access.
    Only admins can suspend users.
    """
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.update_user_status(db, user_id, "suspended")
    return {"message": "User suspended successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Activate a suspended user.
    Only admins can activate users.
    """
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.update_user_status(db, user_id, "active")
    return {"message": "User activated successfully"}