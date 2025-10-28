import psutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models.schemas import SystemStats, SystemHealth, LogEntry
from models.request import Request

async def get_system_stats(db: AsyncSession) -> SystemStats:
    """Get current system resource usage and performance metrics."""
    # Get system resource usage
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Calculate requests per minute
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    result = await db.execute(
        select(func.count(Request.id))
        .where(Request.created_at >= one_minute_ago)
    )
    requests_last_minute = result.scalar() or 0
    
    # Calculate average response time for completed requests in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.avg(Request.processing_time))
        .where(
            Request.status == "completed",
            Request.created_at >= one_hour_ago
        )
    )
    avg_response_time = result.scalar() or 0.0

    return SystemStats(
        cpu_usage=cpu_usage,
        memory_usage=memory.percent,
        disk_usage=disk.percent,
        requests_per_minute=float(requests_last_minute),
        avg_response_time=float(avg_response_time)
    )

async def get_system_health(db: AsyncSession) -> SystemHealth:
    """Check health status of all system components."""
    components = {}
    
    # Check database
    try:
        await db.execute(select(1))
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = "down"
        logging.error(f"Database health check failed: {str(e)}")
    
    # Add other component checks here (Redis, external services, etc.)
    
    # Determine overall status
    if "down" in components.values():
        status = "down"
    elif "degraded" in components.values():
        status = "degraded"
    else:
        status = "healthy"
    
    return SystemHealth(
        status=status,
        components=components,
        last_check=datetime.utcnow()
    )

async def get_logs(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    level: Optional[str] = None,
    limit: int = 100
) -> List[LogEntry]:
    """Get system logs from the logging system."""
    # This is a placeholder. In a real system, you would:
    # 1. Either query logs from a logging database (e.g., Elasticsearch)
    # 2. Or read and parse log files
    # 3. Or use a logging service API
    
    # For now, we'll return an empty list
    # TODO: Implement actual log retrieval
    return []