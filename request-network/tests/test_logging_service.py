"""تست‌های مربوط به سرویس لاگینگ"""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.logging import LoggingService
from api.schemas.logging import (
    LogEntryCreate, ErrorLogCreate, ErrorLogUpdate,
    AuditLogCreate, PerformanceLogCreate, LogFilter
)


@pytest.mark.asyncio
async def test_create_log(db_session: AsyncSession):
    """تست ایجاد لاگ جدید"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    log_data = LogEntryCreate(
        level="info",
        message="تست لاگ",
        source="test_module",
        trace_id=str(uuid.uuid4()),
        metadata={"test_key": "test_value"}
    )

    log = await service.create_log(log_data, user_id)

    assert log.level == log_data.level
    assert log.message == log_data.message
    assert log.source == log_data.source
    assert log.trace_id == log_data.trace_id
    assert log.metadata == log_data.metadata
    assert log.user_id == user_id
    assert log.id is not None
    assert isinstance(log.timestamp, datetime)


@pytest.mark.asyncio
async def test_list_logs(db_session: AsyncSession):
    """تست دریافت لیست لاگ‌ها"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    # ایجاد چند لاگ برای تست
    for i in range(3):
        log_data = LogEntryCreate(
            level="info",
            message=f"تست لاگ {i}",
            source="test_module"
        )
        await service.create_log(log_data, user_id)

    log_filter = LogFilter(
        start_time=datetime.utcnow() - timedelta(hours=1),
        end_time=datetime.utcnow(),
        level="info",
        source="test_module"
    )

    logs = await service.list_logs(log_filter)
    assert len(logs) >= 3
    assert all(log.level == "info" for log in logs)
    assert all(log.source == "test_module" for log in logs)


@pytest.mark.asyncio
async def test_create_error_log(db_session: AsyncSession):
    """تست ثبت لاگ خطا"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    error_data = ErrorLogCreate(
        error_type="ValidationError",
        error_message="داده نامعتبر",
        stack_trace="خط ۱۰: خطای اعتبارسنجی",
        source="test_module",
        severity="high",
        status="new",
        metadata={"test_key": "test_value"}
    )

    error_log = await service.create_error_log(error_data, user_id)

    assert error_log.error_type == error_data.error_type
    assert error_log.error_message == error_data.error_message
    assert error_log.severity == error_data.severity
    assert error_log.status == error_data.status
    assert error_log.user_id == user_id
    assert error_log.id is not None
    assert isinstance(error_log.timestamp, datetime)


@pytest.mark.asyncio
async def test_update_error_log(db_session: AsyncSession):
    """تست به‌روزرسانی لاگ خطا"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    # ایجاد یک لاگ خطا
    error_data = ErrorLogCreate(
        error_type="ValidationError",
        error_message="داده نامعتبر",
        source="test_module",
        severity="high",
        status="new"
    )
    error_log = await service.create_error_log(error_data, user_id)

    # به‌روزرسانی لاگ خطا
    update_data = ErrorLogUpdate(
        status="resolved",
        resolution="مشکل حل شد"
    )
    resolved_by = uuid.uuid4()

    updated_log = await service.update_error_log(error_log.id, update_data, resolved_by)

    assert updated_log.status == update_data.status
    assert updated_log.resolution == update_data.resolution
    assert updated_log.resolved_by == resolved_by
    assert isinstance(updated_log.resolved_at, datetime)


@pytest.mark.asyncio
async def test_create_audit_log(db_session: AsyncSession):
    """تست ثبت لاگ تغییرات"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    audit_data = AuditLogCreate(
        action="update",
        entity_type="user",
        entity_id=str(uuid.uuid4()),
        changes={"name": {"old": "قدیمی", "new": "جدید"}},
        metadata={"test_key": "test_value"}
    )

    audit_log = await service.create_audit_log(audit_data, user_id)

    assert audit_log.action == audit_data.action
    assert audit_log.entity_type == audit_data.entity_type
    assert audit_log.entity_id == audit_data.entity_id
    assert audit_log.changes == audit_data.changes
    assert audit_log.user_id == user_id
    assert audit_log.id is not None
    assert isinstance(audit_log.timestamp, datetime)


@pytest.mark.asyncio
async def test_create_performance_log(db_session: AsyncSession):
    """تست ثبت لاگ عملکرد"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    perf_data = PerformanceLogCreate(
        operation="search_users",
        duration_ms=150,
        success=True,
        metadata={"query": "test"}
    )

    perf_log = await service.create_performance_log(perf_data, user_id)

    assert perf_log.operation == perf_data.operation
    assert perf_log.duration_ms == perf_data.duration_ms
    assert perf_log.success == perf_data.success
    assert perf_log.metadata == perf_data.metadata
    assert perf_log.user_id == user_id
    assert perf_log.id is not None
    assert isinstance(perf_log.timestamp, datetime)


@pytest.mark.asyncio
async def test_get_log_summary(db_session: AsyncSession):
    """تست دریافت خلاصه لاگ‌ها"""
    service = LoggingService(db_session)
    user_id = uuid.uuid4()

    # ایجاد لاگ‌های مختلف برای تست
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()

    # ایجاد لاگ‌های عادی
    for level in ["error", "warning", "info", "debug"]:
        log_data = LogEntryCreate(
            level=level,
            message=f"تست لاگ {level}",
            source="test_module"
        )
        await service.create_log(log_data, user_id)

    # ایجاد لاگ‌های عملکرد
    for i in range(3):
        perf_data = PerformanceLogCreate(
            operation="test_operation",
            duration_ms=100 + i * 50,
            success=True
        )
        await service.create_performance_log(perf_data, user_id)

    summary = await service.get_log_summary(start_time, end_time)

    assert summary.total_logs >= 4  # حداقل یکی از هر سطح
    assert summary.error_count >= 1
    assert summary.warning_count >= 1
    assert summary.info_count >= 1
    assert summary.debug_count >= 1
    assert summary.average_response_time > 0
    assert isinstance(summary.error_rate, float)
    assert summary.start_time == start_time
    assert summary.end_time >= end_time