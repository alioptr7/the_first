from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_

from ..auth.dependencies import get_current_active_user, get_current_admin_user
from ..core.dependencies import get_db as get_db_session
from ..models.request_type import RequestType, RequestTypeParameter
from ..models.user import User
from ..schemas.request_type import RequestTypeCreate, RequestTypeRead, RequestTypeUpdate

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
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """List all request types."""
    query = select(RequestType).options(
        selectinload(RequestType.parameters),
        selectinload(RequestType.access_rules)
    )
    
    if not include_inactive:
        query = query.filter(RequestType.is_active == True)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{request_type_id}", response_model=RequestTypeRead)
async def get_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific request type by ID."""
    query = select(RequestType).options(
        selectinload(RequestType.parameters),
        selectinload(RequestType.access_rules)
    ).filter(RequestType.id == request_type_id)
    
    result = await session.execute(query)
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    if not request_type.is_active:
        raise HTTPException(status_code=404, detail="Request type is not active")
    
    return request_type


@router.patch("/{request_type_id}", response_model=RequestTypeRead)
async def update_request_type(
    request_type_id: UUID,
    update_data: RequestTypeUpdate,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a request type (admin only)."""
    # Get existing request type
    query = select(RequestType).options(
        selectinload(RequestType.parameters)
    ).filter(RequestType.id == request_type_id)
    
    result = await session.execute(query)
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    # Update basic fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key != "parameters":  # Handle parameters separately
            setattr(request_type, key, value)
    
    # Update parameters if provided
    if "parameters" in update_dict:
        # Delete existing parameters
        for param in request_type.parameters:
            await session.delete(param)
        
        # Create new parameters
        for param_data in update_data.parameters:
            db_param = RequestTypeParameter(**param_data.model_dump(), request_type=request_type)
            session.add(db_param)
    
    await session.commit()
    await session.refresh(request_type)
    
    return request_type


@router.delete("/{request_type_id}", status_code=204)
async def delete_request_type(
    request_type_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Soft delete a request type by setting is_active=False (admin only)."""
    query = select(RequestType).filter(RequestType.id == request_type_id)
    result = await session.execute(query)
    request_type = result.scalar_one_or_none()
    
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")
    
    request_type.is_active = False
    await session.commit()