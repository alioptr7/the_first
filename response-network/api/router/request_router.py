from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from core.dependencies import get_db
from models.schemas import (
    Request, RequestCreate, RequestUpdate, RequestStats,
    PaginatedResponse
)
from models.user import User
from auth.dependencies import get_current_user
from crud import requests as request_service

router = APIRouter(prefix="/api", tags=["requests"])

@router.get("/requests", response_model=PaginatedResponse)
async def list_requests(
    status: Optional[str] = Query(None, enum=['pending', 'processing', 'completed', 'failed']),
    user_id: Optional[str] = Query(None, description="Filter requests by user ID"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a paginated list of requests with optional status and user filters.
    If user_id is provided, returns requests for that specific user.
    If not provided, returns all requests (admin only).
    """
    # Check if user is trying to access other user's requests
    if user_id and user_id != str(current_user.id) and not current_user.profile_type == 'admin':
        raise HTTPException(
            status_code=403,
            detail="You can only view your own requests"
        )
    
    skip = (page - 1) * size
    # Non-admin users can only see their own requests
    if current_user.profile_type != 'admin':
        user_id = str(current_user.id)
        
    requests = await request_service.get_requests(
        db,
        status=status,
        user_id=user_id,
        skip=skip,
        limit=size
    )
    total = await request_service.get_requests_count(
        db, 
        status=status,
        user_id=user_id
    )
    
    return PaginatedResponse(
        items=requests,
        total=total,
        page=page,
        size=size
    )

@router.get("/requests/{request_id}", response_model=Request)
async def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific request.
    """
    request = await request_service.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request

@router.get("/requests/stats", response_model=RequestStats)
async def get_request_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about requests in the system.
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()

    return await request_service.get_request_stats(db, start_date, end_date)