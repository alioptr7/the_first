"""روترهای مربوط به سیستم لاگینگ"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.database import get_db
from api.dependencies.auth import get_current_user
from api.models.user import User
from api.schemas.logging import (
    LogEntryCreate, LogEntryRead, ErrorLogCreate, ErrorLogRead,
    ErrorLogUpdate, AuditLogCreate, AuditLogRead, PerformanceLogCreate,
    PerformanceLogRead, LogFilter, LogSummary
)
from api.services.logging import LoggingService

router = APIRouter(prefix="/logging", tags=["logging"])


@router.post("/logs", response_model=LogEntryRead)
async def create_log(
    log: LogEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ایجاد یک لاگ جدید"""
    logging_service = LoggingService(db)
    return await logging_service.create_log(log, current_user.id)


@router.get("/logs", response_model=List[LogEntryRead])
async def list_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    source: Optional[str] = None,
    user_id: Optional[UUID] = None,
    request_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست لاگ‌ها با فیلتر"""
    logging_service = LoggingService(db)
    log_filter = LogFilter(
        start_time=start_time,
        end_time=end_time,
        level=level,
        source=source,
        user_id=user_id,
        request_id=request_id
    )
    return await logging_service.list_logs(log_filter, skip, limit)


@router.post("/errors", response_model=ErrorLogRead)
async def create_error_log(
    error_log: ErrorLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ثبت یک لاگ خطا"""
    logging_service = LoggingService(db)
    return await logging_service.create_error_log(error_log, current_user.id)


@router.get("/errors", response_model=List[ErrorLogRead])
async def list_error_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    error_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    request_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست لاگ‌های خطا با فیلتر"""
    logging_service = LoggingService(db)
    return await logging_service.list_error_logs(
        start_time, end_time, error_type, severity,
        status, user_id, request_id, skip, limit
    )


@router.patch("/errors/{error_id}", response_model=ErrorLogRead)
async def update_error_log(
    error_id: UUID,
    update_data: ErrorLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی وضعیت یک لاگ خطا"""
    logging_service = LoggingService(db)
    return await logging_service.update_error_log(error_id, update_data, current_user.id)


@router.post("/audit", response_model=AuditLogRead)
async def create_audit_log(
    audit_log: AuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ثبت یک لاگ تغییرات"""
    logging_service = LoggingService(db)
    return await logging_service.create_audit_log(audit_log, current_user.id)


@router.get("/audit", response_model=List[AuditLogRead])
async def list_audit_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست لاگ‌های تغییرات با فیلتر"""
    logging_service = LoggingService(db)
    return await logging_service.list_audit_logs(
        start_time, end_time, action, entity_type,
        entity_id, user_id, skip, limit
    )


@router.post("/performance", response_model=PerformanceLogRead)
async def create_performance_log(
    performance_log: PerformanceLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ثبت یک لاگ عملکرد"""
    logging_service = LoggingService(db)
    return await logging_service.create_performance_log(performance_log, current_user.id)


@router.get("/performance", response_model=List[PerformanceLogRead])
async def list_performance_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    operation: Optional[str] = None,
    success: Optional[bool] = None,
    user_id: Optional[UUID] = None,
    request_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست لاگ‌های عملکرد با فیلتر"""
    logging_service = LoggingService(db)
    return await logging_service.list_performance_logs(
        start_time, end_time, operation, success,
        user_id, request_id, skip, limit
    )


@router.get("/summary", response_model=LogSummary)
async def get_log_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت خلاصه لاگ‌ها"""
    logging_service = LoggingService(db)
    return await logging_service.get_log_summary(start_time, end_time)