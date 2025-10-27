from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from models.request import Request
from models.schemas import RequestStats

async def get_requests(
    db: Session,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Request]:
    query = db.query(Request)
    if status:
        query = query.filter(Request.status == status)
    return query.order_by(Request.created_at.desc()).offset(skip).limit(limit).all()

async def get_requests_count(
    db: Session,
    status: Optional[str] = None
) -> int:
    query = db.query(Request)
    if status:
        query = query.filter(Request.status == status)
    return query.count()

async def get_request(db: Session, request_id: int) -> Optional[Request]:
    return db.query(Request).filter(Request.id == request_id).first()

async def get_request_stats(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> RequestStats:
    base_query = db.query(Request).filter(
        Request.created_at.between(start_date, end_date)
    )

    total = base_query.count()
    pending = base_query.filter(Request.status == "pending").count()
    processing = base_query.filter(Request.status == "processing").count()
    completed = base_query.filter(Request.status == "completed").count()
    failed = base_query.filter(Request.status == "failed").count()
    
    avg_time = db.query(func.avg(Request.processing_time))\
        .filter(
            Request.status.in_(["completed", "failed"]),
            Request.created_at.between(start_date, end_date)
        ).scalar() or 0.0

    return RequestStats(
        total=total,
        pending=pending,
        processing=processing,
        completed=completed,
        failed=failed,
        avg_processing_time=float(avg_time)
    )