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


@pytest.mark.asyncio
async def test_authentication_errors(
    app: FastAPI,
    client: AsyncClient,
    expired_admin_token: Dict[str, str],
    non_admin_token: Dict[str, str]
):
    """تست خطاهای احراز هویت"""
    # تست بدون توکن
    response = await client.get(f"{settings.API_V1_STR}/admin/stats/requests")
    assert response.status_code == 401

    # تست با توکن نامعتبر
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

    # تست با توکن منقضی شده
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=expired_admin_token
    )
    assert response.status_code == 401

    # تست با کاربر غیر ادمین
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=non_admin_token
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_request_stats(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار درخواست‌ها"""
    now = datetime.utcnow()
    
    # ایجاد درخواست‌های تستی با زمان‌های مختلف
    requests = []
    statuses = ["pending", "completed", "failed", "completed"]
    query_types = ["match", "search", "match", "search"]
    
    for i, (status, query_type) in enumerate(zip(statuses, query_types)):
        request = Request(
            user_id=uuid.uuid4(),
            name=f"Test Request {status}",
            query_type=query_type,
            query_params={"field": "test"},
            status=status,
            created_at=now - timedelta(days=i),
        )
        if status == "completed":
            request.result_received_at = request.created_at + timedelta(minutes=5)
        db_session.add(request)
        requests.append(request)
    await db_session.commit()

    # تست بدون فیلتر
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=admin_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 4
    assert data["pending_requests"] == 1
    assert data["completed_requests"] == 2
    assert data["failed_requests"] == 1
    assert "average_processing_time" in data

    # تست با فیلتر زمانی
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=admin_token,
        params={
            "start_date": (now - timedelta(days=1)).isoformat(),
            "end_date": now.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 2

    # تست با فیلتر نوع درخواست
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/requests",
        headers=admin_token,
        params={"query_type": "match"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 2


@pytest.mark.asyncio
async def test_get_user_stats(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار کاربران"""
    now = datetime.utcnow()
    
    # ایجاد کاربران تستی با وضعیت‌های مختلف
    users = []
    for i in range(4):
        user = User(
            username=f"test_user_{i}",
            email=f"test{i}@example.com",
            hashed_password="test_hash",
            last_login_at=now - timedelta(days=i * 20),
            is_active=i < 3  # یک کاربر غیرفعال
        )
        db_session.add(user)
        users.append(user)
    await db_session.commit()

    # ایجاد درخواست‌های تستی برای کاربران
    for i, user in enumerate(users):
        for j in range(i):  # هر کاربر تعداد متفاوتی درخواست دارد
            request = Request(
                user_id=user.id,
                name="Test Request",
                query_type="match",
                query_params={"field": "test"},
                status="completed",
                created_at=now - timedelta(days=j)
            )
            db_session.add(request)
    await db_session.commit()

    # تست بدون فیلتر
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/users",
        headers=admin_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 4
    assert data["active_users"] == 3
    assert len(data["top_users"]) > 0
    assert data["top_users"][0]["request_count"] == 3  # کاربر اول بیشترین درخواست را دارد

    # تست با فیلتر زمانی
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/users",
        headers=admin_token,
        params={
            "start_date": (now - timedelta(days=10)).isoformat(),
            "end_date": now.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active_users"] < 4  # تعداد کاربران فعال در بازه زمانی کمتر است


@pytest.mark.asyncio
async def test_get_system_stats(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API دریافت آمار سیستمی"""
    now = datetime.utcnow()
    
    # ایجاد درخواست‌های تستی با وضعیت‌ها و زمان‌های مختلف
    statuses = ["completed", "completed", "failed", "pending", "completed"]
    processing_times = [5, 10, None, None, None]  # برخی درخواست‌ها زمان پردازش ندارند
    
    for status, proc_time in zip(statuses, processing_times):
        request = Request(
            user_id=uuid.uuid4(),
            name=f"Test Request {status}",
            query_type="match",
            query_params={"field": "test"},
            status=status,
            created_at=now - timedelta(minutes=15)
        )
        if proc_time is not None:
            request.result_received_at = request.created_at + timedelta(minutes=proc_time)
        db_session.add(request)
    await db_session.commit()

    # تست بدون فیلتر
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/system",
        headers=admin_token
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_request_types" in data
    assert "average_response_time" in data
    assert "system_success_rate" in data
    assert data["system_success_rate"] == pytest.approx(60.0, rel=0.01)  # 3/5 درخواست‌ها موفق
    assert data["average_response_time"] > 0  # میانگین زمان پردازش باید مثبت باشد

    # تست با فیلتر زمانی
    response = await client.get(
        f"{settings.API_V1_STR}/admin/stats/system",
        headers=admin_token,
        params={
            "start_date": (now - timedelta(minutes=10)).isoformat(),
            "end_date": now.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] < 5  # تعداد درخواست‌ها در بازه زمانی کمتر است


@pytest.mark.asyncio
async def test_batch_request_action(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    admin_token: Dict[str, str]
):
    """تست API عملیات دسته‌ای روی درخواست‌ها"""
    # ایجاد درخواست‌های تستی با وضعیت‌های مختلف
    request_ids = {
        "failed": [],
        "pending": [],
        "completed": []
    }
    
    for status in request_ids.keys():
        for _ in range(2):
            request = Request(
                user_id=uuid.uuid4(),
                name=f"Test Request {status}",
                query_type="match",
                query_params={"field": "test"},
                status=status,
                retry_count=1 if status == "failed" else 0
              )
            db_session.add(request)
            await db_session.commit()
            request_ids[status].append(request.id)

    # تست retry درخواست‌های ناموفق
    response = await client.post(
        f"{settings.API_V1_STR}/admin/requests/batch",
        headers=admin_token,
        json={
            "action": "retry",
            "request_ids": [str(id) for id in request_ids["failed"]],
            "reason": "تست retry"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # بررسی به‌روزرسانی درخواست‌ها
    for request_id in request_ids["failed"]:
        request = await db_session.get(Request, request_id)
        assert request.status == "pending"
        assert request.retry_count == 2
        assert request.error_message is None

    # تست cancel درخواست‌های در حال انجام
    response = await client.post(
        f"{settings.API_V1_STR}/admin/requests/batch",
        headers=admin_token,
        json={
            "action": "cancel",
            "request_ids": [str(id) for id in request_ids["pending"]],
            "reason": "تست cancel"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # بررسی به‌روزرسانی درخواست‌ها
    for request_id in request_ids["pending"]:
        request = await db_session.get(Request, request_id)
        assert request.status == "cancelled"

    # تست عملیات روی درخواست‌های ناموجود
    response = await client.post(
        f"{settings.API_V1_STR}/admin/requests/batch",
        headers=admin_token,
        json={
            "action": "retry",
            "request_ids": [str(uuid.uuid4())],
            "reason": "تست درخواست ناموجود"
        }
    )
    assert response.status_code == 404

    # تست عملیات نامعتبر روی درخواست‌ها
    response = await client.post(
        f"{settings.API_V1_STR}/admin/requests/batch",
        headers=admin_token,
        json={
            "action": "retry",
            "request_ids": [str(id) for id in request_ids["completed"]],
            "reason": "تست عملیات نامعتبر"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_action_log(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    admin_token: Dict[str, str],
    admin_user: User
):
    """تست API‌های لاگ اکشن‌های ادمین"""
    now = datetime.utcnow()
    
    # ایجاد چند لاگ اکشن تستی
    action_types = ["retry", "cancel", "delete"]
    target_types = ["request", "user", "batch"]
    
    for i, (action_type, target_type) in enumerate(zip(action_types, target_types)):
        log_entry = AdminActionLog(
            admin_id=admin_user.id,
            action_type=action_type,
            target_type=target_type,
            target_ids=[str(uuid.uuid4()) for _ in range(2)],
            details={"test_key": f"test_value_{i}"},
            created_at=now - timedelta(days=i)
        )
        db_session.add(log_entry)
    await db_session.commit()

    # تست دریافت لاگ‌ها بدون فیلتر
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3

    # تست فیلتر بر اساس نوع عملیات
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token,
        params={"action_type": "retry"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["action_type"] == "retry"

    # تست فیلتر بر اساس نوع هدف
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token,
        params={"target_type": "request"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["target_type"] == "request"

    # تست فیلتر زمانی
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token,
        params={
            "start_date": (now - timedelta(days=1)).isoformat(),
            "end_date": now.isoformat()
        }
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 2

    # تست صفحه‌بندی
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log",
        headers=admin_token,
        params={"skip": 1, "limit": 1}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1

    # تست دریافت جزئیات یک لاگ
    log_id = logs[0]["id"]
    response = await client.get(
        f"{settings.API_V1_STR}/admin/action-log/{log_id}",
        headers=admin_token
    )
    assert response.status_code == 200
    log_detail = response.json()
    assert "details" in log_detail
    assert "created_at" in log_detail