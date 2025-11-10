from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, delete, and_

from core.dependencies import get_db
from models.schemas import UserCreate, UserUpdate, User, UserWithStats
from models.user import User as UserModel
from models.request_type import RequestType
from models.request_access import UserRequestAccess
from auth.dependencies import get_current_admin_user
from crud import users as user_service
from schemas.request_access import UserRequestAccessCreate, UserRequestAccessRead

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

@router.get("/me", response_model=UserWithStats)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get detailed information about the currently authenticated user including their request statistics.
    """
    return await user_service.get_user_with_stats(db, current_user.id)

@router.get("/{user_id}", response_model=UserWithStats)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get detailed information about a specific user."""
    return await user_service.get_user_with_stats(db, user_id)


@router.post("/{user_id}/request-access", response_model=List[UserRequestAccessRead])
async def grant_request_type_access(
    user_id: UUID,
    request_types: List[UserRequestAccessCreate],
    current_user: UserModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Grant access to multiple request types for a user.
    Only admin users can grant access.
    """
    # Verify user exists
    user = await session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Verify request types exist
    request_type_ids = [rt.request_type_id for rt in request_types]
    result = await session.execute(
        select(RequestType).where(RequestType.id.in_(request_type_ids))
    )
    found_types = {rt.id: rt for rt in result.scalars().all()}
    
    missing_types = set(request_type_ids) - set(found_types.keys())
    if missing_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request types not found: {', '.join(str(rid) for rid in missing_types)}"
        )
    
    # Remove existing access for these request types
    await session.execute(
        delete(UserRequestAccess).where(and_(
            UserRequestAccess.user_id == user_id,
            UserRequestAccess.request_type_id.in_(request_type_ids)
        ))
    )
    
    # Create new access records
    access_records = []
    for rt_access in request_types:
        access = UserRequestAccess(
            user_id=user_id,
            request_type_id=rt_access.request_type_id,
            max_requests_per_hour=rt_access.max_requests_per_hour,
            is_active=rt_access.is_active
        )
        session.add(access)
        access_records.append(access)
    
    await session.commit()
    for record in access_records:
        await session.refresh(record)
    
    return access_records


@router.get("/{user_id}/request-access", response_model=List[UserRequestAccessRead])
async def list_user_request_access(
    user_id: UUID,
    current_user: UserModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db)
):
    """
    List all request types that this user has access to.
    Only admin users can view access list.
    """
    result = await session.execute(
        select(UserRequestAccess)
        .where(UserRequestAccess.user_id == user_id)
    )
    return result.scalars().all()


@router.delete("/{user_id}/request-access/{request_type_id}")
async def revoke_request_type_access(
    user_id: UUID,
    request_type_id: UUID,
    current_user: UserModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Revoke access to a request type from this user.
    Only admin users can revoke access.
    """
    result = await session.execute(
        delete(UserRequestAccess).where(and_(
            UserRequestAccess.user_id == user_id,
            UserRequestAccess.request_type_id == request_type_id
        ))
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No access found for request type {request_type_id} for user {user_id}"
        )
    
    await session.commit()
    return {"status": "success"}
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