"""User router"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_user
from api.db.session import get_db
from api.models.user import User
from api.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update current user information"""
    # Check if username or email is being changed and already exists
    if user_update.username or user_update.email:
        query = select(User).where(
            (User.id != current_user.id)
            & (
                (User.username == (user_update.username or current_user.username))
                | (User.email == (user_update.email or current_user.email))
            )
        )
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user