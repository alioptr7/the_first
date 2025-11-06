from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_

from ..auth.dependencies import get_current_admin_user, get_current_user
from ..db.session import get_db_session
from ..models.request_type import RequestType, RequestTypeParameter
from ..models.user import User
from ..schemas.request_type import (
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
    session: AsyncSession = Depends(get_db_session)
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
    
    # Access rules are not modeled in ORM; ensure empty list for response
    db_request_type.access_rules = []
    
    await session.commit()
    await session.refresh(db_request_type)
    
    return db_request_type


@router.get("", response_model=List[RequestTypeRead])
async def list_request_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """List request types available to the current user."""
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters)
        )
    )
    
    # Filter by active status unless explicitly including inactive
    if not include_inactive:
        query = query.where(RequestType.is_active == True)
    
    # Access rules filtering is disabled pending proper ORM mapping
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    items = result.scalars().all()
    # Ensure attribute exists for response schema compatibility
    for it in items:
        setattr(it, "access_rules", [])
    return items


@router.get("/{request_type_id}", response_model=RequestTypeRead)
async def get_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific request type by ID."""
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters)
        )
        .where(RequestType.id == request_type_id)
    )
    
    result = await session.execute(query)
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    # Access checks based on rules are disabled pending proper ORM mapping
    # Ensure attribute exists for response schema compatibility
    setattr(request_type, "access_rules", [])
    
    return request_type


@router.put("/{request_type_id}", response_model=RequestTypeRead)
async def update_request_type(
    request_type_id: UUID,
    request_type_update: RequestTypeUpdate,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a request type (admin only)."""
    # Get existing request type
    query = (
        select(RequestType)
        .options(
            selectinload(RequestType.parameters)
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
    
    # Access rules updates are disabled pending proper ORM mapping
    if request_type_update.access_rules is not None:
        db_request_type.access_rules = []
    
    await session.commit()
    await session.refresh(db_request_type)
    
    # Ensure attribute exists for response schema compatibility
    db_request_type.access_rules = []
    return db_request_type


@router.delete("/{request_type_id}", status_code=204)
async def delete_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session)
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
