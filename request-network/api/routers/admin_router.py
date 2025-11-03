"""Admin router module"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.core.config import settings
from api.db.session import get_db
from api.models.user import User
from api.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all users"""
    query = await db.execute(
        User.__table__.select().offset(skip).limit(limit)
    )
    users = query.fetchall()
    return [UserResponse.from_orm(user) for user in users]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a user"""
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a user"""
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(db_user)
    await db.commit()
    return None