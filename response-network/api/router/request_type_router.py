from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_

from api.auth.dependencies import get_current_admin_user, get_current_user
from api.db.session import get_session
from api.models.request_type import RequestType, RequestTypeParameter, RequestTypeAccess
from api.models.user import User
from api.schemas.request_type import (
    RequestTypeCreate,
    RequestTypeRead,
    RequestTypeUpdate,
    RequestTypeParameterRead,
    RequestTypeAccessRead
)

router = APIRouter(prefix="/request-types", tags=["request-types"])


@router.post("", response_model=RequestTypeRead)
async def create_request_type(
    request_type: RequestTypeCreate,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new request type (admin only)."""
    # Create request type
    db_request_type = RequestType(
        **request_type.model_dump(exclude={"parameters", "access_rules"}),
        created_by_id=current_user.id
    )
    session.add(db_request_type)
    
    # Create parameters
    for param in request_type.parameters:
        db_param = RequestTypeParameter(**param.model_dump(), request_type=db_request_type)
        session.add(db_param)
    
    # Create access rules
    if request_type.access_rules:
        for rule in request_type.access_rules:
            db_rule = RequestTypeAccess(**rule.model_dump(), request_type=db_request_type)
            session.add(db_rule)
    
    await session.commit()
    await session.refresh(db_request_type)
    
    return db_request_type


@router.get("", response_model=List[RequestTypeRead])
async def list_request_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List request types available to the current user."""
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters),
            selectinload(RequestType.access_rules)
        )
    )
    
    # Filter by active status unless explicitly including inactive
    if not include_inactive:
        query = query.where(RequestType.is_active == True)
    
    # For non-admin users, filter by access rules
    if not current_user.is_admin:
        query = query.join(RequestTypeAccess).where(
            and_(
                RequestTypeAccess.is_active == True,
                RequestTypeAccess.profile_type == current_user.profile_type
            )
        )
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{request_type_id}", response_model=RequestTypeRead)
async def get_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific request type by ID."""
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters),
            selectinload(RequestType.access_rules)
        )
        .where(RequestType.id == request_type_id)
    )
    
    result = await session.execute(query)
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    # Check access for non-admin users
    if not current_user.is_admin:
        has_access = False
        for rule in request_type.access_rules:
            if rule.is_active and (
                rule.user_id == current_user.id or
                any(rule.role_id == role.id for role in current_user.roles)
            ):
                has_access = True
                break
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return request_type


@router.put("/{request_type_id}", response_model=RequestTypeRead)
async def update_request_type(
    request_type_id: UUID,
    request_type_update: RequestTypeUpdate,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """Update a request type (admin only)."""
    # Get existing request type
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters),
            selectinload(RequestType.access_rules)
        )
        .where(RequestType.id == request_type_id)
    )
    result = await session.execute(query)
    db_request_type = result.scalar_one_or_none()
    
    if not db_request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    # Update basic fields
    update_data = request_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field not in {"parameters", "access_rules"}:
            setattr(db_request_type, field, value)
    
    # Update parameters if provided
    if request_type_update.parameters is not None:
        # Remove existing parameters
        for param in db_request_type.parameters:
            await session.delete(param)
        
        # Create new parameters
        for param in request_type_update.parameters:
            db_param = RequestTypeParameter(**param.model_dump(), request_type=db_request_type)
            session.add(db_param)
    
    # Update access rules if provided
    if request_type_update.access_rules is not None:
        # Remove existing rules
        for rule in db_request_type.access_rules:
            await session.delete(rule)
        
        # Create new rules
        for rule in request_type_update.access_rules:
            db_rule = RequestTypeAccess(**rule.model_dump(), request_type=db_request_type)
            session.add(db_rule)
    
    await session.commit()
    await session.refresh(db_request_type)
    
    return db_request_type


@router.delete("/{request_type_id}", status_code=204)
async def delete_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a request type (admin only)."""
    result = await session.execute(
        select(RequestType).where(RequestType.id == request_type_id)
    )
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    await session.delete(request_type)
    await session.commit()