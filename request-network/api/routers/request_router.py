import json
import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from api.core.validation import validate_request_payload
from api.db.session import get_db_session
from api.models.user import User
from api.models.request import Request
from api.auth.dependencies import get_current_active_user
# from rate_limiter import check_rate_limit  # TODO: Fix rate limiter
from api.schemas.request import RequestCreate, RequestPublic, RequestStatus
from api.schemas.response_detail import ResponseDetail
from api.core.redis import get_cached_response, cache_response

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "/",
    response_model=RequestPublic,
    status_code=status.HTTP_201_CREATED)
async def submit_request(
    request_data: RequestCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Submit a new request for processing.

    This endpoint handles:
    1. Unique name validation
    2. Service (index) access verification
    3. Request creation with elasticsearch query parameters
    """
    # 1. Check if request name is unique
    existing_request = await db.execute(
        select(Request).where(Request.name == request_data.name)
    )
    if existing_request.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request with name '{request_data.name}' already exists"
        )

    # 2. Check if user has access to the requested service/index
    allowed_indices = json.loads(current_user.allowed_indices)
    if request_data.request.serviceName not in allowed_indices:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to service: {request_data.request.serviceName}"
        )

    # 3. Create request object
    new_request = Request(
        user_id=current_user.id,
        name=request_data.name,
        query_type=request_data.request.serviceName,
        query_params=request_data.request.fieldRequest.model_dump(),
        priority=current_user.priority,  # Inherit priority from user profile
        status=request_data.reqState,
    )
    
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)

    return new_request


@router.get("/", response_model=List[RequestPublic])
async def get_user_requests(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of requests submitted by the current user.
    """
    query = (
        select(Request)
        .where(Request.user_id == current_user.id)
        .order_by(Request.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    requests = result.scalars().all()
    return requests


async def get_request_or_404(
    request_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    load_response: bool = False,
) -> Request:
    """Dependency to get a request and check ownership."""
    query = select(Request).where(Request.id == request_id)
    if load_response:
        query = query.options(selectinload(Request.response))

    result = await db.execute(query)
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    # A real app might allow admins to see any request, but for now, only owners can.
    if request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this request")

    return request


@router.get("/{request_id}", response_model=RequestPublic)
async def get_request_details(
    request_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve the full details of a specific request, including its response if available.
    """
    request = await get_request_or_404(request_id, current_user, db, load_response=True)
    return request


@router.get("/{request_id}/status", response_model=RequestStatus)
async def get_request_status(
    request_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve just the status of a specific request (lightweight).
    """
    request = await get_request_or_404(request_id, current_user, db)
    return request


@router.get("/{request_id}/response", response_model=ResponseDetail)
async def get_request_response(
    request_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve the complete response data for a specific request.
    First checks Redis cache, then falls back to database if not found.
    """
    # بررسی وجود درخواست و دسترسی کاربر
    request = await get_request_or_404(request_id, current_user, db, load_response=True)
    
    # اگر درخواست هنوز پاسخی ندارد
    if not request.response:
        raise HTTPException(
            status_code=404,
            detail="Response not available yet"
        )
    
    # بررسی کش Redis
    cached_response = get_cached_response(str(request_id))
    if cached_response:
        # به‌روزرسانی فیلد is_cached
        request.response.is_cached = True
        return request.response
    
    # اگر در کش نبود، از دیتابیس می‌خوانیم و در کش ذخیره می‌کنیم
    request.response.is_cached = False
    response_data = {
        "id": request.response.id,
        "request_id": request.response.request_id,
        "result_data": request.response.result_data,
        "result_count": request.response.result_count,
        "execution_time_ms": request.response.execution_time_ms,
        "received_at": request.response.received_at.isoformat(),
        "is_cached": False,
        "meta": request.response.meta
    }
    cache_response(str(request_id), response_data)
    
    return request.response


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
@router.post(
    "/{request_id}/cancel",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_request(
    request_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Cancel a request. A request can only be cancelled if its status is 'pending'.
    """
    request = await get_request_or_404(request_id, current_user, db)

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel request with status '{request.status}'",
        )

    request.status = "cancelled"
    db.add(request)
    await db.commit()

    return None