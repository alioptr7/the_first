import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.session import get_db_session
from ..auth.dependencies import require_admin
from ..models.user import User
from ..schemas.user import UserSchema

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)


@router.get("/users", response_model=List[UserSchema])
async def list_users(
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = Query(None, description="Filter by active status"),
    profile_type: str | None = Query(None, description="Filter by profile type"),
):
    """
    List all users in the system. Admins only.
    Supports pagination and filtering.
    """
    query = select(User)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if profile_type:
        query = query.where(User.profile_type == profile_type)

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get detailed information for a specific user. Admins only.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/users/{user_id}/activate", response_model=UserSchema)
async def activate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Activate a user account. Admins only.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active")

    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserSchema)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Deactivate a user account. Admins only.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already inactive")

    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user