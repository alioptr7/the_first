"""تست‌های مربوط به API‌های لاگینگ"""
import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from api.models.logging import LogEntry, ErrorLog, AuditLog, PerformanceLog
from api.schemas.logging import (
    LogEntryCreate, ErrorLogCreate, ErrorLogUpdate,
    AuditLogCreate, PerformanceLogCreate
)


@pytest.mark.asyncio
async def test_create_log(
    async_client: AsyncClient,
    normal_user_token: str
):
    """تست ایجاد لاگ جدید"""
    log_data = {
        "level": "info",
        "message": "تست لاگ",
        "source": "test_module",
        "trace_id": str(uuid.uuid4()),
        "metadata": {"test_key": "test_value"}
    }

    response = await async_client.post(
        "/logging/logs",
        json=log_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == log_data["level"]
    assert data["message"] == log_data["message"]
    assert data["source"] == log_data["source"]
    assert data["trace_id"] == log_data["trace_id"]
    assert data["metadata"] == log_data["metadata"]
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_list_logs(
    async_client: AsyncClient,
    normal_user_token: str,
    db_session
):
    """تست دریافت لیست لاگ‌ها"""
    # ایجاد چند لاگ برای تست
    logs = []
    for i in range(3):
        log = LogEntry(
            level="info",
            message=f"تست لاگ {i}",
            source="test_module",
            user_id=uuid.uuid4()
        )
        db_session.add(log)
        logs.append(log)
    await db_session.commit()

    response = await async_client.get(
        "/logging/logs",
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all(isinstance(log["id"], str) for log in data)


@pytest.mark.asyncio
async def test_create_error_log(
    async_client: AsyncClient,
    normal_user_token: str
):
    """تست ثبت لاگ خطا"""
    error_data = {
        "error_type": "ValidationError",
        "error_message": "داده نامعتبر",
        "stack_trace": "خط ۱۰: خطای اعتبارسنجی",
        "source": "test_module",
        "severity": "high",
        "status": "new",
        "metadata": {"test_key": "test_value"}
    }

    response = await async_client.post(
        "/logging/errors",
        json=error_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["error_type"] == error_data["error_type"]
    assert data["error_message"] == error_data["error_message"]
    assert data["severity"] == error_data["severity"]
    assert data["status"] == error_data["status"]
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_update_error_log(
    async_client: AsyncClient,
    normal_user_token: str,
    db_session
):
    """تست به‌روزرسانی لاگ خطا"""
    # ایجاد یک لاگ خطا برای به‌روزرسانی
    error_log = ErrorLog(
        error_type="ValidationError",
        error_message="داده نامعتبر",
        source="test_module",
        severity="high",
        status="new",
        user_id=uuid.uuid4()
    )
    db_session.add(error_log)
    await db_session.commit()

    update_data = {
        "status": "resolved",
        "resolution": "مشکل حل شد"
    }

    response = await async_client.patch(
        f"/logging/errors/{error_log.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["resolution"] == update_data["resolution"]
    assert "resolved_at" in data
    assert data["resolved_at"] is not None


@pytest.mark.asyncio
async def test_create_audit_log(
    async_client: AsyncClient,
    normal_user_token: str
):
    """تست ثبت لاگ تغییرات"""
    audit_data = {
        "action": "update",
        "entity_type": "user",
        "entity_id": str(uuid.uuid4()),
        "changes": {"name": {"old": "قدیمی", "new": "جدید"}},
        "metadata": {"test_key": "test_value"}
    }

    response = await async_client.post(
        "/logging/audit",
        json=audit_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == audit_data["action"]
    assert data["entity_type"] == audit_data["entity_type"]
    assert data["entity_id"] == audit_data["entity_id"]
    assert data["changes"] == audit_data["changes"]
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_create_performance_log(
    async_client: AsyncClient,
    normal_user_token: str
):
    """تست ثبت لاگ عملکرد"""
    perf_data = {
        "operation": "search_users",
        "duration_ms": 150,
        "success": True,
        "metadata": {"query": "test"}
    }

    response = await async_client.post(
        "/logging/performance",
        json=perf_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == perf_data["operation"]
    assert data["duration_ms"] == perf_data["duration_ms"]
    assert data["success"] == perf_data["success"]
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_log_summary(
    async_client: AsyncClient,
    normal_user_token: str,
    db_session
):
    """تست دریافت خلاصه لاگ‌ها"""
    # ایجاد لاگ‌های مختلف برای تست
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()

    # ایجاد لاگ‌های عادی
    for level in ["error", "warning", "info", "debug"]:
        log = LogEntry(
            level=level,
            message=f"تست لاگ {level}",
            source="test_module",
            user_id=uuid.uuid4(),
            timestamp=datetime.utcnow()
        )
        db_session.add(log)

    # ایجاد لاگ‌های عملکرد
    for i in range(3):
        perf_log = PerformanceLog(
            operation="test_operation",
            duration_ms=100 + i * 50,
            success=True,
            user_id=uuid.uuid4(),
            timestamp=datetime.utcnow()
        )
        db_session.add(perf_log)

    await db_session.commit()

    response = await async_client.get(
        "/logging/summary",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_logs"] >= 4  # حداقل یکی از هر سطح
    assert data["error_count"] >= 1
    assert data["warning_count"] >= 1
    assert data["info_count"] >= 1
    assert data["debug_count"] >= 1
    assert data["average_response_time"] > 0
    assert isinstance(data["error_rate"], float)
    assert "start_time" in data
    assert "end_time" in data