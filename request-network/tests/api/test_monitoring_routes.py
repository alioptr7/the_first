"""تست‌های مربوط به API‌های مانیتورینگ"""
import uuid
from datetime import datetime, timedelta
from typing import Dict

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.monitoring import (
    SystemMetrics, ServiceHealth, ErrorLog,
    PerformanceMetrics, ResourceUsage
)
from api.models.user import User
from api.core.config import settings


@pytest.fixture
def admin_token(admin_user: User) -> Dict[str, str]:
    """فیکسچر توکن ادمین"""
    return {"Authorization": f"Bearer {admin_user.generate_token()}"}


@pytest.mark.asyncio
async def test_create_system_metrics(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API ثبت متریک‌های سیستمی"""
    metrics_data = {
        "metric_name": "cpu_usage",
        "metric_type": "system",
        "metric_value": 45.5,
        "unit": "percent",
        "tags": {"host": "server-1"}
    }

    response = await client.post(
        f"{settings.API_V1_STR}/monitoring/metrics/system",
        headers=admin_token,
        json=metrics_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["metric_name"] == metrics_data["metric_name"]
    assert data["metric_value"] == metrics_data["metric_value"]


@pytest.mark.asyncio
async def test_list_system_metrics(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت لیست متریک‌های سیستمی"""
    # ایجاد چند متریک تستی
    metrics = []
    for i in range(3):
        metric = SystemMetrics(
            metric_name=f"test_metric_{i}",
            metric_type="system",
            metric_value=float(i * 10),
            unit="percent",
            tags={"test": "true"}
        )
        session.add(metric)
        metrics.append(metric)
    await session.commit()

    # تست فیلترهای مختلف
    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/metrics/system",
        headers=admin_token,
        params={"metric_type": "system"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # تست فیلتر زمانی
    start_time = datetime.utcnow() - timedelta(hours=1)
    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/metrics/system",
        headers=admin_token,
        params={"start_time": start_time.isoformat()}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_update_service_health(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API به‌روزرسانی وضعیت سلامت سرویس"""
    health_data = {
        "service_name": "api_service",
        "status": "healthy",
        "details": {
            "uptime": 3600,
            "response_time": 150
        }
    }

    response = await client.post(
        f"{settings.API_V1_STR}/monitoring/health",
        headers=admin_token,
        json=health_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == health_data["service_name"]
    assert data["status"] == health_data["status"]


@pytest.mark.asyncio
async def test_list_service_health(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت وضعیت سلامت سرویس‌ها"""
    # ایجاد چند وضعیت سلامت تستی
    services = []
    for status in ["healthy", "degraded", "unhealthy"]:
        service = ServiceHealth(
            service_name=f"test_service_{status}",
            status=status,
            details={"test": "true"}
        )
        session.add(service)
        services.append(service)
    await session.commit()

    # تست فیلترهای مختلف
    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/health",
        headers=admin_token,
        params={"status": "healthy"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "healthy"


@pytest.mark.asyncio
async def test_log_error(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API ثبت خطا"""
    error_data = {
        "error_type": "api_error",
        "service_name": "api_service",
        "severity": "high",
        "message": "Test error message",
        "details": {
            "endpoint": "/test",
            "method": "GET"
        }
    }

    response = await client.post(
        f"{settings.API_V1_STR}/monitoring/errors",
        headers=admin_token,
        json=error_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["error_type"] == error_data["error_type"]
    assert data["severity"] == error_data["severity"]


@pytest.mark.asyncio
async def test_list_errors(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت لیست خطاها"""
    # ایجاد چند خطای تستی
    errors = []
    for severity in ["low", "medium", "high"]:
        error = ErrorLog(
            error_type="test_error",
            service_name="test_service",
            severity=severity,
            message=f"Test error {severity}",
            details={"test": "true"}
        )
        session.add(error)
        errors.append(error)
    await session.commit()

    # تست فیلترهای مختلف
    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/errors",
        headers=admin_token,
        params={"severity": "high"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["severity"] == "high"


@pytest.mark.asyncio
async def test_get_metrics_summary(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت خلاصه متریک‌ها"""
    # ایجاد داده‌های تستی برای متریک‌های مختلف
    # متریک‌های عملکرد
    for _ in range(3):
        perf_metric = PerformanceMetrics(
            endpoint="/test",
            method="GET",
            response_time_ms=100,
            status_code=200
        )
        session.add(perf_metric)

    # مصرف منابع
    for resource in ["cpu", "memory", "disk", "network"]:
        usage = ResourceUsage(
            resource_type=resource,
            usage_value=45.5,
            unit="percent"
        )
        session.add(usage)

    # وضعیت سلامت سرویس‌ها
    for service in ["api", "worker", "db"]:
        health = ServiceHealth(
            service_name=service,
            status="healthy",
            details={"uptime": 3600}
        )
        session.add(health)

    await session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/summary",
        headers=admin_token
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "average_response_time" in data
    assert "error_rate" in data
    assert "success_rate" in data
    assert "resource_usage" in data
    assert "service_health" in data


@pytest.mark.asyncio
async def test_get_time_range_metrics(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت متریک‌ها در بازه زمانی"""
    # ایجاد متریک‌های تستی در بازه‌های زمانی مختلف
    base_time = datetime.utcnow() - timedelta(hours=2)
    for i in range(4):
        metric = SystemMetrics(
            metric_name="test_metric",
            metric_type="system",
            metric_value=float(i * 10),
            unit="percent",
            timestamp=base_time + timedelta(minutes=30 * i)
        )
        session.add(metric)
    await session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/monitoring/metrics/time-range",
        headers=admin_token,
        params={
            "start_time": base_time.isoformat(),
            "end_time": (base_time + timedelta(hours=2)).isoformat(),
            "interval": "hour",
            "metric_names": ["test_metric"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "labels" in data
    assert "test_metric" in data["metrics"]
    assert len(data["metrics"]["test_metric"]) == 4