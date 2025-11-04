from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import func, and_, select

from models.request import Request
from models.query_result import QueryResult
from models.schemas import (
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
    total_count_query = select(func.count()).select_from(request_query.with_only_columns(Request.id).subquery())
    successful_query = select(func.count()).select_from(request_query.where(Request.status == "completed").with_only_columns(Request.id).subquery())
    failed_query = select(func.count()).select_from(request_query.where(Request.status == "failed").with_only_columns(Request.id).subquery())

    total_count = (await db.execute(total_count_query)).scalar_one()
    successful = (await db.execute(successful_query)).scalar_one()
    failed = (await db.execute(failed_query)).scalar_one()
    
    avg_response_time_query = select(func.avg(QueryResult.execution_time_ms)).where(
        QueryResult.request_id.in_(request_query.with_only_columns(Request.id))
    )
    
    avg_response_time = (await db.execute(avg_response_time_query)).scalar() or 0.0

    return RequestStats(
        total_count=total_count,
        successful_count=successful,
        failed_count=failed,
        average_response_time=float(avg_response_time)
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
    return SystemStats(
        cpu_usage=0.0,
        memory_usage=0.0,
        disk_usage=0.0,
        network_latency=0.0
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