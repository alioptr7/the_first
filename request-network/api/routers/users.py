"""
Users router for Request Network - Read-only access to synced users
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from db.session import get_db_session
from models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    profile_type: str
    is_active: bool
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    daily_request_limit: int
    monthly_request_limit: int
    priority: int
    synced_at: datetime | None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all synced users in Request Network
    """
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific user by ID
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a user by username
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

