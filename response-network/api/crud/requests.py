from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import List, Optional
from datetime import datetime

from models.request import Request
from models.schemas import RequestStats

async def get_requests(
    db: AsyncSession,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Request]:
    query = select(Request)
    if status:
        query = query.where(Request.status == status)
    if user_id:
        query = query.where(Request.user_id == user_id)
    query = query.order_by(Request.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_requests_count(
    db: AsyncSession,
    status: Optional[str] = None,
    user_id: Optional[str] = None
) -> int:
    query = select(func.count()).select_from(Request)
    if status:
        query = query.where(Request.status == status)
    if user_id:
        query = query.where(Request.user_id == user_id)
    result = await db.execute(query)
    return result.scalar() or 0

async def get_request(
    db: AsyncSession, 
    request_id: int
) -> Optional[Request]:
    query = select(Request).where(Request.id == request_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_request_stats(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> RequestStats:
    # Base query for total count
    total_query = select(func.count()).select_from(Request).where(
        Request.created_at.between(start_date, end_date)
    )
    result = await db.execute(total_query)
    total = result.scalar() or 0

    # Status-specific counts
    status_counts = {}
    for status_type in ["pending", "processing", "completed", "failed"]:
        query = select(func.count()).select_from(Request).where(
            Request.created_at.between(start_date, end_date),
            Request.status == status_type
        )
        result = await db.execute(query)
        status_counts[status_type] = result.scalar() or 0

    # Average processing time
    avg_query = select(func.avg(Request.processing_time)).select_from(Request).where(
        Request.status.in_(["completed", "failed"]),
        Request.created_at.between(start_date, end_date)
    )
    result = await db.execute(avg_query)
    avg_time = float(result.scalar() or 0.0)

    return RequestStats(
        total=total,
        pending=status_counts["pending"],
        processing=status_counts["processing"],
        completed=status_counts["completed"],
        failed=status_counts["failed"],
        avg_processing_time=avg_time
    )