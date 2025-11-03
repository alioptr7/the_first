"""Monitoring router"""
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin_user
from api.db.session import get_db
from api.models.task_logs import TaskLog
from api.models.user import User
from api.schemas.logging import LogFilter, LogResponse

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/logs", response_model=List[LogResponse])
async def get_logs(
    filter_params: Annotated[LogFilter, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
) -> List[LogResponse]:
    """Get logs with filtering"""
    query = select(TaskLog)

    if filter_params.start_time:
        query = query.where(TaskLog.created_at >= filter_params.start_time)
    if filter_params.end_time:
        query = query.where(TaskLog.created_at <= filter_params.end_time)
    if filter_params.service_name:
        query = query.where(TaskLog.service_name == filter_params.service_name)
    if filter_params.log_type:
        query = query.where(TaskLog.log_type == filter_params.log_type)
    if filter_params.user_id:
        query = query.where(TaskLog.user_id == filter_params.user_id)
    if filter_params.severity:
        query = query.where(TaskLog.severity == filter_params.severity)
    if filter_params.status:
        query = query.where(TaskLog.status == filter_params.status)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [LogResponse.model_validate(log) for log in logs]