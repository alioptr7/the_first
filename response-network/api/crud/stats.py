from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_, select

from ..models.request import Request
from ..models.query_result import QueryResult
from ..models.model_schemas import (
    RequestStats,
    QueryStats,
    SystemHealth,
    SystemStats,
    LogEntry
)

async def get_request_stats(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> RequestStats:
    """Get statistics about requests processed by the response network."""
    request_query = select(Request)
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        request_query = request_query.where(Request.created_at >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        request_query = request_query.where(Request.created_at <= end)

    # To get counts, we create subqueries
    total_query = select(func.count()).select_from(request_query.with_only_columns(Request.id).subquery())
    pending_query = select(func.count()).select_from(request_query.where(Request.status == "pending").with_only_columns(Request.id).subquery())
    processing_query = select(func.count()).select_from(request_query.where(Request.status == "processing").with_only_columns(Request.id).subquery())
    completed_query = select(func.count()).select_from(request_query.where(Request.status == "completed").with_only_columns(Request.id).subquery())
    failed_query = select(func.count()).select_from(request_query.where(Request.status == "failed").with_only_columns(Request.id).subquery())

    total = (await db.execute(total_query)).scalar_one()
    pending = (await db.execute(pending_query)).scalar_one()
    processing = (await db.execute(processing_query)).scalar_one()
    completed = (await db.execute(completed_query)).scalar_one()
    failed = (await db.execute(failed_query)).scalar_one()
    
    request_ids = [req.id for req in (await db.execute(request_query)).scalars().all()]
    
    if request_ids:
        avg_response_time_query = select(func.avg(QueryResult.execution_time_ms)).where(
            QueryResult.request_id.in_(request_ids)
        )
        avg_response_time = (await db.execute(avg_response_time_query)).scalar() or 0.0
    else:
        avg_response_time = 0.0

    return RequestStats(
        total=total,
        pending=pending,
        processing=processing,
        completed=completed,
        failed=failed,
        avg_processing_time=float(avg_response_time)
    )

async def get_query_stats(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> QueryStats:
    """Get statistics about queries processed by the response network."""
    # Similar implementation as request stats but for queries
    # This will be implemented when the Query model is finalized
    return QueryStats(
        total_count=0,
        successful_count=0,
        failed_count=0,
        average_processing_time=0.0
    )

async def get_system_health(db: Session) -> SystemHealth:
    """Get current system health status."""
    # Check various system components and return health status
    # This will integrate with monitoring tools/services
    return SystemHealth(
        status="healthy",
        components={
            "database": "healthy",
            "cache": "healthy",
            "search": "healthy"
        },
        last_check=datetime.now(timezone.utc)
    )

async def get_system_stats(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> SystemStats:
    """Get system performance statistics."""
    # Collect system performance metrics
    # This will integrate with monitoring tools/services
    
    request_stats = await get_request_stats(db, start_date, end_date)
    
    total_requests = request_stats.total
    
    # Calculate time difference for requests_per_minute
    if start_date and end_date:
        time_diff = datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)
        minutes = time_diff.total_seconds() / 60
        requests_per_minute = total_requests / minutes if minutes > 0 else 0
    else:
        # If no date range, calculate over the last hour
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)
        
        request_query = select(func.count(Request.id)).where(
            and_(Request.created_at >= start, Request.created_at <= end)
        )
        
        total_requests_last_hour = (await db.execute(request_query)).scalar_one()
        requests_per_minute = total_requests_last_hour / 60
        
    return SystemStats(
        cpu_usage=0.0,
        memory_usage=0.0,
        disk_usage=0.0,
        network_latency=0.0,
        requests_per_minute=requests_per_minute,
        avg_response_time=request_stats.avg_processing_time
    )

async def get_logs(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[LogEntry]:
    """Get system logs with filtering options."""
    # Implement log retrieval from logging system
    # This will integrate with logging service
    return []
