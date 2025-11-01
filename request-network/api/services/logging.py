"""سرویس مدیریت لاگ‌ها"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.logging import LogEntry, ErrorLog, AuditLog, PerformanceLog
from api.schemas.logging import (
    LogEntryCreate, ErrorLogCreate, ErrorLogUpdate,
    AuditLogCreate, PerformanceLogCreate, LogFilter, LogSummary
)


class LoggingService:
    """کلاس سرویس مدیریت لاگ‌ها"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(self, log: LogEntryCreate, user_id: UUID) -> LogEntry:
        """ایجاد یک لاگ جدید"""
        db_log = LogEntry(
            level=log.level,
            message=log.message,
            source=log.source,
            trace_id=log.trace_id,
            request_id=log.request_id,
            user_id=user_id,
            metadata=log.metadata
        )
        self.db.add(db_log)
        await self.db.commit()
        await self.db.refresh(db_log)
        return db_log

    async def list_logs(
        self,
        log_filter: LogFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[LogEntry]:
        """دریافت لیست لاگ‌ها با فیلتر"""
        query = select(LogEntry)

        if log_filter.start_time:
            query = query.filter(LogEntry.timestamp >= log_filter.start_time)
        if log_filter.end_time:
            query = query.filter(LogEntry.timestamp <= log_filter.end_time)
        if log_filter.level:
            query = query.filter(LogEntry.level == log_filter.level)
        if log_filter.source:
            query = query.filter(LogEntry.source == log_filter.source)
        if log_filter.user_id:
            query = query.filter(LogEntry.user_id == log_filter.user_id)
        if log_filter.request_id:
            query = query.filter(LogEntry.request_id == log_filter.request_id)

        query = query.order_by(LogEntry.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_error_log(
        self,
        error_log: ErrorLogCreate,
        user_id: UUID
    ) -> ErrorLog:
        """ثبت یک لاگ خطا"""
        db_error = ErrorLog(
            error_type=error_log.error_type,
            error_message=error_log.error_message,
            stack_trace=error_log.stack_trace,
            source=error_log.source,
            severity=error_log.severity,
            status=error_log.status,
            resolution=error_log.resolution,
            request_id=error_log.request_id,
            user_id=user_id,
            metadata=error_log.metadata
        )
        self.db.add(db_error)
        await self.db.commit()
        await self.db.refresh(db_error)
        return db_error

    async def list_error_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ErrorLog]:
        """دریافت لیست لاگ‌های خطا با فیلتر"""
        query = select(ErrorLog)

        if start_time:
            query = query.filter(ErrorLog.timestamp >= start_time)
        if end_time:
            query = query.filter(ErrorLog.timestamp <= end_time)
        if error_type:
            query = query.filter(ErrorLog.error_type == error_type)
        if severity:
            query = query.filter(ErrorLog.severity == severity)
        if status:
            query = query.filter(ErrorLog.status == status)
        if user_id:
            query = query.filter(ErrorLog.user_id == user_id)
        if request_id:
            query = query.filter(ErrorLog.request_id == request_id)

        query = query.order_by(ErrorLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_error_log(
        self,
        error_id: UUID,
        update_data: ErrorLogUpdate,
        resolved_by: UUID
    ) -> ErrorLog:
        """به‌روزرسانی وضعیت یک لاگ خطا"""
        query = select(ErrorLog).filter(ErrorLog.id == error_id)
        result = await self.db.execute(query)
        error_log = result.scalar_one_or_none()

        if not error_log:
            raise ValueError("لاگ خطا یافت نشد")

        if update_data.status:
            error_log.status = update_data.status
        if update_data.resolution:
            error_log.resolution = update_data.resolution
            error_log.resolved_at = datetime.utcnow()
            error_log.resolved_by = resolved_by

        await self.db.commit()
        await self.db.refresh(error_log)
        return error_log

    async def create_audit_log(
        self,
        audit_log: AuditLogCreate,
        user_id: UUID
    ) -> AuditLog:
        """ثبت یک لاگ تغییرات"""
        db_audit = AuditLog(
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            user_id=user_id,
            changes=audit_log.changes,
            metadata=audit_log.metadata
        )
        self.db.add(db_audit)
        await self.db.commit()
        await self.db.refresh(db_audit)
        return db_audit

    async def list_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """دریافت لیست لاگ‌های تغییرات با فیلتر"""
        query = select(AuditLog)

        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        query = query.order_by(AuditLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_performance_log(
        self,
        performance_log: PerformanceLogCreate,
        user_id: UUID
    ) -> PerformanceLog:
        """ثبت یک لاگ عملکرد"""
        db_perf = PerformanceLog(
            operation=performance_log.operation,
            duration_ms=performance_log.duration_ms,
            success=performance_log.success,
            error_message=performance_log.error_message,
            request_id=performance_log.request_id,
            user_id=user_id,
            metadata=performance_log.metadata
        )
        self.db.add(db_perf)
        await self.db.commit()
        await self.db.refresh(db_perf)
        return db_perf

    async def list_performance_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        operation: Optional[str] = None,
        success: Optional[bool] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PerformanceLog]:
        """دریافت لیست لاگ‌های عملکرد با فیلتر"""
        query = select(PerformanceLog)

        if start_time:
            query = query.filter(PerformanceLog.timestamp >= start_time)
        if end_time:
            query = query.filter(PerformanceLog.timestamp <= end_time)
        if operation:
            query = query.filter(PerformanceLog.operation == operation)
        if success is not None:
            query = query.filter(PerformanceLog.success == success)
        if user_id:
            query = query.filter(PerformanceLog.user_id == user_id)
        if request_id:
            query = query.filter(PerformanceLog.request_id == request_id)

        query = query.order_by(PerformanceLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_log_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> LogSummary:
        """دریافت خلاصه لاگ‌ها"""
        # پایه کوئری برای همه لاگ‌ها
        base_query = select(LogEntry)
        if start_time:
            base_query = base_query.filter(LogEntry.timestamp >= start_time)
        if end_time:
            base_query = base_query.filter(LogEntry.timestamp <= end_time)

        # محاسبه تعداد کل لاگ‌ها
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(total_query)
        total_logs = total_result.scalar()

        # محاسبه تعداد لاگ‌ها بر اساس سطح
        level_counts = {}
        for level in ["error", "warning", "info", "debug"]:
            level_query = select(func.count()).select_from(
                base_query.filter(LogEntry.level == level).subquery()
            )
            level_result = await self.db.execute(level_query)
            level_counts[level] = level_result.scalar()

        # محاسبه میانگین زمان پاسخ
        perf_query = select(func.avg(PerformanceLog.duration_ms))
        if start_time:
            perf_query = perf_query.filter(PerformanceLog.timestamp >= start_time)
        if end_time:
            perf_query = perf_query.filter(PerformanceLog.timestamp <= end_time)
        perf_result = await self.db.execute(perf_query)
        avg_response_time = perf_result.scalar() or 0.0

        # محاسبه نرخ خطا
        error_rate = (level_counts["error"] / total_logs * 100) if total_logs > 0 else 0

        return LogSummary(
            total_logs=total_logs,
            error_count=level_counts["error"],
            warning_count=level_counts["warning"],
            info_count=level_counts["info"],
            debug_count=level_counts["debug"],
            average_response_time=avg_response_time,
            error_rate=error_rate,
            start_time=start_time or datetime.min,
            end_time=end_time or datetime.utcnow()
        )