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
    client: AsyncClient,
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

    response = await client.post(
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
    client: AsyncClient,
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

    response = await client.get(
        "/logging/logs",
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all(isinstance(log["id"], str) for log in data)


@pytest.mark.asyncio
async def test_create_error_log(
    client: AsyncClient,
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

    response = await client.post(
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
    client: AsyncClient,
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

    response = await client.patch(
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
    client: AsyncClient,
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

    response = await client.post(
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
    client: AsyncClient,
    normal_user_token: str
):
    """تست ثبت لاگ عملکرد"""
    perf_data = {
        "operation": "search_users",
        "duration_ms": 150,
        "success": True,
        "metadata": {"query": "test"}
    }

    response = await client.post(
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


"""تست‌های مربوط به API‌های لاگینگ"""
import pytest
from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ConfigDict

from api.models.monitoring import (
    SystemMetrics, ServiceHealth, ErrorLog,
    PerformanceMetrics, ResourceUsage
)
from api.schemas.monitoring import (
    SystemMetricsCreate, ServiceHealthCreate,
    ErrorLogCreate, PerformanceMetricsCreate,
    ResourceUsageCreate
)


@pytest.mark.asyncio
async def test_create_system_metrics(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست ایجاد متریک‌های سیستمی"""
    metrics_data = {
        "metric_name": "cpu_usage",
        "metric_type": "gauge",
        "metric_value": 45.5,
        "unit": "percent",
        "extra_data": {"host": "server1"}
    }

    # تست ایجاد متریک با کاربر ادمین
    response = await async_client.post(
        "/monitoring/metrics/system",
        json=metrics_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["metric_name"] == metrics_data["metric_name"]
    assert data["metric_value"] == metrics_data["metric_value"]
    assert "id" in data
    assert "timestamp" in data

    # تست ایجاد متریک با کاربر غیر ادمین
    response = await async_client.post(
        "/monitoring/metrics/system",
        json=metrics_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_system_metrics(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست دریافت لیست متریک‌های سیستمی"""
    # ایجاد چند متریک برای تست
    metrics = []
    for i in range(3):
        metric = SystemMetrics(
            metric_name=f"metric_{i}",
            metric_type="gauge",
            metric_value=i * 10.0,
            unit="percent",
            extra_data={"test": f"value_{i}"}
        )
        db_session.add(metric)
        metrics.append(metric)
    await db_session.commit()

    # تست دریافت همه متریک‌ها
    response = await async_client.get(
        "/monitoring/metrics/system",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

    # تست فیلتر بر اساس نام متریک
    response = await async_client.get(
        "/monitoring/metrics/system?metric_name=metric_0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["metric_name"] == "metric_0"

    # تست محدودیت تعداد نتایج
    response = await async_client.get(
        "/monitoring/metrics/system?limit=2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # تست فیلتر زمانی
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()
    response = await async_client.get(
        f"/monitoring/metrics/system?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_service_health(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست به‌روزرسانی وضعیت سلامت سرویس"""
    health_data = {
        "service_name": "api_service",
        "status": "healthy",
        "details": {"uptime": "24h", "response_time": "45ms"},
        "last_check": datetime.utcnow().isoformat()
    }

    # تست ایجاد وضعیت سلامت
    response = await async_client.post(
        "/monitoring/health",
        json=health_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == health_data["service_name"]
    assert data["status"] == health_data["status"]

    # تست به‌روزرسانی به وضعیت ناسالم
    health_data["status"] = "unhealthy"
    health_data["details"]["error"] = "Connection timeout"
    response = await async_client.post(
        "/monitoring/health",
        json=health_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert "error" in data["details"]


@pytest.mark.asyncio
async def test_list_service_health(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست دریافت وضعیت سلامت سرویس‌ها"""
    # ایجاد وضعیت سلامت برای چند سرویس
    services = ["api", "worker", "database"]
    statuses = ["healthy", "unhealthy", "degraded"]
    
    for i, (service, status) in enumerate(zip(services, statuses)):
        health = ServiceHealth(
            service_name=service,
            status=status,
            details={"check": f"test_{i}"},
            last_check=datetime.utcnow()
        )
        db_session.add(health)
    await db_session.commit()

    # تست دریافت همه سرویس‌ها
    response = await async_client.get(
        "/monitoring/health",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

    # تست فیلتر بر اساس نام سرویس
    response = await async_client.get(
        "/monitoring/health?service_name=api",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["service_name"] == "api"

    # تست فیلتر بر اساس وضعیت
    response = await async_client.get(
        "/monitoring/health?status=healthy",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "healthy" for item in data)


@pytest.mark.asyncio
async def test_log_error(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست ثبت خطا"""
    error_data = {
        "error_type": "ValidationError",
        "error_message": "داده نامعتبر",
        "stack_trace": "خط ۱۰: خطای اعتبارسنجی",
        "service_name": "api",
        "severity": "high",
        "status": "new",
        "extra_data": {"test_key": "test_value"}
    }

    # تست ثبت خطا
    response = await async_client.post(
        "/monitoring/errors",
        json=error_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["error_type"] == error_data["error_type"]
    assert data["severity"] == error_data["severity"]

    # تست ثبت خطا با جزئیات کامل
    error_data.update({
        "error_type": "DatabaseError",
        "error_message": "خطای اتصال به دیتابیس",
        "stack_trace": "جزئیات کامل خطا...",
        "service_name": "database",
        "severity": "critical",
        "status": "investigating",
        "resolution": "در حال بررسی توسط تیم فنی",
        "extra_data": {
            "connection_id": "db_001",
            "attempt": 3,
            "last_successful": "2024-03-15T10:00:00Z"
        }
    })
    response = await async_client.post(
        "/monitoring/errors",
        json=error_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "critical"
    assert "resolution" in data
    assert "extra_data" in data


@pytest.mark.asyncio
async def test_list_errors(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست دریافت لیست خطاها"""
    # ایجاد چند خطا با انواع مختلف
    error_types = ["ValidationError", "DatabaseError", "NetworkError"]
    severities = ["low", "medium", "high"]
    
    for i, (error_type, severity) in enumerate(zip(error_types, severities)):
        error = ErrorLog(
            error_type=error_type,
            error_message=f"خطای تست {i}",
            service_name="test_service",
            severity=severity,
            status="new",
            timestamp=datetime.utcnow()
        )
        db_session.add(error)
    await db_session.commit()

    # تست دریافت همه خطاها
    response = await async_client.get(
        "/monitoring/errors",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

    # تست فیلتر بر اساس نوع خطا
    response = await async_client.get(
        "/monitoring/errors?error_type=ValidationError",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["error_type"] == "ValidationError"

    # تست فیلتر بر اساس شدت خطا
    response = await async_client.get(
        "/monitoring/errors?severity=high",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["severity"] == "high" for item in data)

    # تست فیلتر زمانی
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()
    response = await async_client.get(
        f"/monitoring/errors?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_metrics_summary(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست دریافت خلاصه متریک‌ها"""
    # ایجاد داده‌های تست
    # متریک‌های عملکرد
    for i in range(5):
        perf = PerformanceMetrics(
            endpoint="/test",
            method="GET",
            response_time_ms=100 + i * 10,
            status_code=200 if i < 4 else 500,
            timestamp=datetime.utcnow()
        )
        db_session.add(perf)

    # مصرف منابع
    resources = ["cpu", "memory", "disk", "network"]
    for resource in resources:
        usage = ResourceUsage(
            resource_type=resource,
            usage_value=45.5,
            timestamp=datetime.utcnow()
        )
        db_session.add(usage)

    # وضعیت سلامت سرویس‌ها
    services = ["api", "worker", "database"]
    for service in services:
        health = ServiceHealth(
            service_name=service,
            status="healthy",
            last_check=datetime.utcnow()
        )
        db_session.add(health)

    await db_session.commit()

    # تست دریافت خلاصه
    response = await async_client.get(
        "/monitoring/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()

    # بررسی فیلدهای اصلی
    assert "total_requests" in data
    assert "average_response_time" in data
    assert "error_rate" in data
    assert "success_rate" in data
    assert "resource_usage" in data
    assert "service_health" in data
    assert "timestamp" in data

    # بررسی محاسبات
    assert data["total_requests"] >= 5
    assert data["average_response_time"] > 0
    assert 0 <= data["error_rate"] <= 100
    assert 0 <= data["success_rate"] <= 100
    assert data["error_rate"] + data["success_rate"] == 100

    # بررسی مصرف منابع
    assert len(data["resource_usage"]) == 4
    for resource in resources:
        assert resource in data["resource_usage"]

    # بررسی وضعیت سرویس‌ها
    assert len(data["service_health"]) == 3
    for service in services:
        assert service in data["service_health"]


@pytest.mark.asyncio
async def test_get_time_range_metrics(
    async_client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession
):
    """تست دریافت متریک‌ها در بازه زمانی"""
    # ایجاد داده‌های تست در بازه‌های زمانی مختلف
    base_time = datetime.utcnow() - timedelta(hours=24)
    metric_names = ["cpu_usage", "memory_usage"]
    
    for hour in range(24):
        for metric_name in metric_names:
            metric = SystemMetrics(
                metric_name=metric_name,
                metric_type="gauge",
                metric_value=45.5 + hour,
                unit="percent",
                timestamp=base_time + timedelta(hours=hour)
            )
            db_session.add(metric)
    await db_session.commit()

    # تست با بازه زمانی معتبر
    start_time = base_time
    end_time = datetime.utcnow()
    response = await async_client.get(
        f"/monitoring/metrics/time-range?start_time={start_time.isoformat()}"
        f"&end_time={end_time.isoformat()}&interval=hour"
        f"&metric_names={','.join(metric_names)}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # بررسی ساختار پاسخ
    assert "start_time" in data
    assert "end_time" in data
    assert "interval" in data
    assert "metrics" in data
    assert "labels" in data

    # بررسی داده‌های متریک‌ها
    for metric_name in metric_names:
        assert metric_name in data["metrics"]
        assert metric_name in data["labels"]
        assert len(data["metrics"][metric_name]) > 0
        assert len(data["labels"][metric_name]) > 0
        assert len(data["metrics"][metric_name]) == len(data["labels"][metric_name])

    # تست با بازه زمانی نامعتبر
    response = await async_client.get(
        f"/monitoring/metrics/time-range?start_time={end_time.isoformat()}"
        f"&end_time={start_time.isoformat()}&interval=hour"
        f"&metric_names={','.join(metric_names)}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

    # تست با فاصله زمانی نامعتبر
    response = await async_client.get(
        f"/monitoring/metrics/time-range?start_time={start_time.isoformat()}"
        f"&end_time={end_time.isoformat()}&interval=invalid"
        f"&metric_names={','.join(metric_names)}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422  # Validation Error