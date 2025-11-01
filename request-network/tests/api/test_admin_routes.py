"""تست‌های مربوط به API‌های پنل ادمین"""
import uuid
from datetime import datetime, timedelta
from typing import Dict

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.request import Request
from api.models.user import User
from api.models.admin_action import AdminActionLog
from api.core.config import settings


@pytest.fixture
def admin_token(admin_user: User) -> Dict[str, str]:
    """فیکسچر توکن ادمین"""
    return {"Authorization": f"Bearer {admin_user.generate_token()}"}


@pytest.mark.asyncio
async def test_get_request_stats(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار درخواست‌ها"""
    # ایجاد چند درخواست تستی
    requests = []
    for status in ["pending", "completed", "failed"]:
        request = Request(
            user_id=uuid.uuid4(),
            name=f"Test Request {status}",
            query_type="match",
            query_params={"field": "test"},
            status=status,
            created_at=datetime.utcnow()
        )
        if status == "completed":
            request.result_received_at = datetime.utcnow() + timedelta(minutes=5)
        session.add(request)
        requests.append(request)
    await session.commit()

    # فراخوانی API
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=admin_token
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 3
    assert data["pending_requests"] == 1
    assert data["completed_requests"] == 1
    assert data["failed_requests"] == 1
    assert "average_processing_time" in data


@pytest.mark.asyncio
async def test_get_user_stats(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار کاربران"""
    # ایجاد چند کاربر تستی
    users = []
    for i in range(3):
        user = User(
            username=f"test_user_{i}",
            email=f"test{i}@example.com",
            hashed_password="test_hash",
            last_login_at=datetime.utcnow() if i < 2 else datetime.utcnow() - timedelta(days=40)
        )
        session.add(user)
        users.append(user)
    await session.commit()

    # ایجاد درخواست‌های تستی برای کاربران
    for user in users[:2]:
        for _ in range(2):
            request = Request(
                user_id=user.id,
                name="Test Request",
                query_type="match",
                query_params={"field": "test"},
                status="completed"
            )
            session.add(request)
    await session.commit()

    # فراخوانی API
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/users",
        headers=admin_token
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 3
    assert data["active_users"] == 2
    assert len(data["top_users"]) > 0


@pytest.mark.asyncio
async def test_get_system_stats(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار سیستمی"""
    # ایجاد چند درخواست تستی با وضعیت‌های مختلف
    for status in ["completed", "completed", "failed"]:
        request = Request(
            user_id=uuid.uuid4(),
            name=f"Test Request {status}",
            query_type="match",
            query_params={"field": "test"},
            status=status,
            created_at=datetime.utcnow(),
            result_received_at=datetime.utcnow() + timedelta(minutes=5) if status == "completed" else None
        )
        session.add(request)
    await session.commit()

    # فراخوانی API
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/system",
        headers=admin_token
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_request_types" in data
    assert "average_response_time" in data
    assert "system_success_rate" in data
    assert data["system_success_rate"] == pytest.approx(66.67, rel=0.01)  # 2/3 درخواست‌ها موفق


@pytest.mark.asyncio
async def test_batch_request_action(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API عملیات دسته‌ای روی درخواست‌ها"""
    # ایجاد چند درخواست تستی
    request_ids = []
    for status in ["failed", "failed", "failed"]:
        request = Request(
            user_id=uuid.uuid4(),
            name=f"Test Request {status}",
            query_type="match",
            query_params={"field": "test"},
            status=status
        )
        session.add(request)
        request_ids.append(request.id)
    await session.commit()

    # فراخوانی API برای retry درخواست‌ها
    response = await client.post(
        f"{settings.API_V1_STR}/admin/requests/batch",
        headers=admin_token,
        json={
            "action": "retry",
            "request_ids": [str(id) for id in request_ids],
            "reason": "تست عملیات دسته‌ای"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # بررسی به‌روزرسانی درخواست‌ها
    for request_id in request_ids:
        request = await session.get(Request, request_id)
        assert request.status == "pending"
        assert request.retry_count == 1
        assert request.error_message is None


@pytest.mark.asyncio
async def test_admin_action_log(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    admin_token: Dict[str, str],
    admin_user: User
):
    """تست API‌های لاگ اکشن‌های ادمین"""
    # ایجاد یک لاگ اکشن تستی
    action_data = {
        "action_type": "test_action",
        "target_type": "request",
        "target_ids": [str(uuid.uuid4()) for _ in range(2)],
        "details": {"test_key": "test_value"}
    }

    # تست ایجاد لاگ
    response = await client.post(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token,
        json=action_data
    )

    assert response.status_code == 200
    created_log = response.json()
    assert created_log["action_type"] == action_data["action_type"]
    assert created_log["target_type"] == action_data["target_type"]

    # تست دریافت لاگ‌ها
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token
    )

    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    assert logs[0]["action_type"] == action_data["action_type"]