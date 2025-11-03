"""User management router"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.db.session import get_db
from api.models.user import User
from api.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """List all users"""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
) -> User:
    """Create a new user"""
    # Check if username or email already exists
    query = select(User).where(
        (User.username == user_create.username) | (User.email == user_create.email)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    user = User(**user_create.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
) -> User:
    """Get a specific user by ID"""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
) -> User:
    """Update a user"""
    # Get existing user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if username or email is being changed and already exists
    if user_update.username or user_update.email:
        query = select(User).where(
            (User.id != user_id)
            & (
                (User.username == (user_update.username or user.username))
                | (User.email == (user_update.email or user.email))
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
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
) -> None:
    """Delete a user"""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()