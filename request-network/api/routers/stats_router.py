"""Statistics router"""
from datetime import datetime, timedelta
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.db.session import get_db
from api.models.task_logs import TaskLog
from api.models.user import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/tasks/summary")
async def get_task_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
    time_range: int = Query(24, description="Time range in hours", ge=1, le=168),
) -> Dict:
    """Get task statistics for the specified time range"""
    start_time = datetime.utcnow() - timedelta(hours=time_range)

    # Total tasks
    total_tasks_query = select(func.count(TaskLog.id)).where(
        TaskLog.created_at >= start_time
    )
    total_tasks_result = await db.execute(total_tasks_query)
    total_tasks = total_tasks_result.scalar() or 0

    # Tasks by status
    status_query = select(
        TaskLog.status,
        func.count(TaskLog.id).label("count")
    ).where(
        TaskLog.created_at >= start_time
    ).group_by(TaskLog.status)
    status_result = await db.execute(status_query)
    status_counts = {row[0]: row[1] for row in status_result}

    # Average completion time
    avg_time_query = select(
        func.avg(
            func.extract("epoch", TaskLog.completed_at - TaskLog.started_at)
        )
    ).where(
        TaskLog.created_at >= start_time,
        TaskLog.completed_at.is_not(None)
    )
    avg_time_result = await db.execute(avg_time_query)
    avg_completion_time = avg_time_result.scalar() or 0

    return {
        "total_tasks": total_tasks,
        "status_counts": status_counts,
        "avg_completion_time_seconds": round(avg_completion_time, 2),
        "time_range_hours": time_range,
    }