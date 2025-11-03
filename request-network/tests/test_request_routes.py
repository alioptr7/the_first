"""تست‌های مربوط به API‌های درخواست‌ها"""
import uuid
from datetime import datetime, timezone
from typing import Dict

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.request import Request
from api.models.user import User
from api.core.config import settings


@pytest.fixture
def sample_request_data() -> Dict:
    """فیکسچر داده‌های نمونه برای ایجاد درخواست"""
    return {
        "name": "test_request",
        "request": {
            "serviceName": "test_service",
            "fieldRequest": {
                "query": "test query",
                "filters": {"field": "value"}
            }
        },
        "reqState": "pending"
    }


@pytest.mark.asyncio
async def test_submit_request_success(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    sample_request_data: Dict
):
    """تست موفق ایجاد درخواست جدید"""
    # تنظیم دسترسی‌های کاربر
    test_user.allowed_indices = '["test_service"]'
    session.add(test_user)
    await session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/requests/",
        headers={"Authorization": f"Bearer {test_user.token}"},
        json=sample_request_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == sample_request_data["name"]
    assert data["query_type"] == sample_request_data["request"]["serviceName"]
    assert data["status"] == sample_request_data["reqState"]
    assert "id" in data


@pytest.mark.asyncio
async def test_submit_request_duplicate_name(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    sample_request_data: Dict
):
    """تست ایجاد درخواست با نام تکراری"""
    # ایجاد یک درخواست با نام مشابه
    existing_request = Request(
        user_id=test_user.id,
        name=sample_request_data["name"],
        query_type="test_service",
        query_params={"test": "data"},
        status="pending"
    )
    session.add(existing_request)
    await session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/requests/",
        headers={"Authorization": f"Bearer {test_user.token}"},
        json=sample_request_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_request_unauthorized_service(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    sample_request_data: Dict
):
    """تست ایجاد درخواست برای سرویس غیرمجاز"""
    # تنظیم دسترسی‌های کاربر به سرویس دیگر
    test_user.allowed_indices = '["other_service"]'
    session.add(test_user)
    await session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/requests/",
        headers={"Authorization": f"Bearer {test_user.token}"},
        json=sample_request_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_requests(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست دریافت لیست درخواست‌های کاربر"""
    # ایجاد چند درخواست برای کاربر
    for i in range(3):
        request = Request(
            user_id=test_user.id,
            name=f"Test Request {i}",
            query_type="test_service",
            query_params={"test": "data"},
            status="pending"
        )
        session.add(request)
    await session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/requests/",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all(req["user_id"] == str(test_user.id) for req in data)


@pytest.mark.asyncio
async def test_get_request_details(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست دریافت جزئیات یک درخواست"""
    # ایجاد یک درخواست
    request = Request(
        user_id=test_user.id,
        name="Test Request",
        query_type="test_service",
        query_params={"test": "data"},
        status="pending"
    )
    session.add(request)
    await session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/requests/{request.id}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(request.id)
    assert data["name"] == request.name
    assert data["status"] == request.status


@pytest.mark.asyncio
async def test_get_request_details_not_found(
    app: FastAPI,
    client: AsyncClient,
    test_user: User
):
    """تست دریافت جزئیات درخواست ناموجود"""
    response = await client.get(
        f"{settings.API_V1_STR}/requests/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_request_details_unauthorized(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    other_user: User
):
    """تست دریافت جزئیات درخواست توسط کاربر غیرمجاز"""
    # ایجاد درخواست برای کاربر اول
    request = Request(
        user_id=test_user.id,
        name="Test Request",
        query_type="test_service",
        query_params={"test": "data"},
        status="pending"
    )
    session.add(request)
    await session.commit()

    # تلاش برای دسترسی با کاربر دوم
    response = await client.get(
        f"{settings.API_V1_STR}/requests/{request.id}",
        headers={"Authorization": f"Bearer {other_user.token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_request_status(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست دریافت وضعیت درخواست"""
    # ایجاد یک درخواست
    request = Request(
        user_id=test_user.id,
        name="Test Request",
        query_type="test_service",
        query_params={"test": "data"},
        status="processing"
    )
    session.add(request)
    await session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/requests/{request.id}/status",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_delete_request(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست حذف درخواست"""
    # ایجاد یک درخواست
    request = Request(
        user_id=test_user.id,
        name="Test Request",
        query_type="test_service",
        query_params={"test": "data"},
        status="pending"
    )
    session.add(request)
    await session.commit()

    response = await client.delete(
        f"{settings.API_V1_STR}/requests/{request.id}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # بررسی حذف درخواست
    deleted_request = await session.get(Request, request.id)
    assert deleted_request is None


@pytest.mark.asyncio
async def test_delete_request_not_found(
    app: FastAPI,
    client: AsyncClient,
    test_user: User
):
    """تست حذف درخواست ناموجود"""
    response = await client.delete(
        f"{settings.API_V1_STR}/requests/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_request_unauthorized(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    other_user: User
):
    """تست حذف درخواست توسط کاربر غیرمجاز"""
    # ایجاد درخواست برای کاربر اول
    request = Request(
        user_id=test_user.id,
        name="Test Request",
        query_type="test_service",
        query_params={"test": "data"},
        status="pending"
    )
    session.add(request)
    await session.commit()

    # تلاش برای حذف با کاربر دوم
    response = await client.delete(
        f"{settings.API_V1_STR}/requests/{request.id}",
        headers={"Authorization": f"Bearer {other_user.token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN