import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..core.validation import validate_request_payload
from ..db.session import get_db_session
from ..models.user import User
from ..models.request import Request
from ..auth.dependencies import get_current_active_user
from ..schemas.request import RequestCreate, RequestPublic, RequestStatus

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("/", response_model=RequestPublic, status_code=status.HTTP_201_CREATED)
async def submit_request(
    request_data: RequestCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db_session),
):
    """
    Submit a new request for processing.

    This is the primary endpoint for users to send their queries to the system.
    The request will be saved with a 'pending' status and processed by a background worker.
    """
    # TODO: Add rate limiting check here before creating the request.

    # Perform validation on the incoming data against the user's profile
    validate_request_payload(request_data, current_user)

    new_request = Request(
        user_id=current_user.id,
        query_type=request_data.query_type,
        query_params=request_data.query_params,
        priority=current_user.priority,  # Inherit priority from user profile
        status="pending",
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


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
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