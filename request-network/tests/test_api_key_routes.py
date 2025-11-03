"""تست‌های مربوط به API‌های مدیریت کلیدهای API"""
from datetime import datetime, timedelta, timezone
import uuid

import pytest
from fastapi import status
from sqlalchemy import select

from api.auth.security import create_access_token
from api.core.config import settings
from api.models.user import User
from api.models.api_key import ApiKey

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.api_key import APIKey
from api.models.user import User
from api.core.config import settings


@pytest.fixture
def api_key_create_data() -> Dict:
    """فیکسچر داده‌های نمونه برای ایجاد کلید API"""
    return {
        "name": "Test API Key",
        "scopes": ["read:requests", "write:requests"]
    }


@pytest.mark.asyncio
async def test_create_api_key(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    api_key_create_data: Dict
):
    """تست ایجاد کلید API جدید"""
    response = await client.post(
        f"{settings.API_V1_STR}/api-keys/",
        headers={"Authorization": f"Bearer {test_user.token}"},
        json=api_key_create_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == api_key_create_data["name"]
    assert "api_key" in data
    assert data["api_key"].startswith("sk_live_")
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_user_api_keys(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """تست دریافت لیست کلیدهای API کاربر"""
    # ایجاد چند کلید API برای کاربر
    for i in range(3):
        api_key = APIKey(
            user_id=test_user.id,
            name=f"Test Key {i}",
            key_hash="test_hash",
            prefix="sk_live_",
            scopes=["read:requests"],
            is_active=True
        )
        db_session.add(api_key)
    await db_session.commit()

    response = await client.get(
        f"{settings.API_V1_STR}/api-keys/",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all(key["user_id"] == str(test_user.id) for key in data)
    assert all("api_key" not in key for key in data)  # کلید اصلی نباید در پاسخ باشد


@pytest.mark.asyncio
async def test_get_user_api_keys_empty(
    app: FastAPI,
    client: AsyncClient,
    test_user: User
):
    """تست دریافت لیست کلیدهای API برای کاربر بدون کلید"""
    response = await client.get(
        f"{settings.API_V1_STR}/api-keys/",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_revoke_api_key(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """تست غیرفعال کردن کلید API"""
    # ایجاد یک کلید API
    api_key = APIKey(
        user_id=test_user.id,
        name="Test Key",
        key_hash="test_hash",
        prefix="sk_live_",
        scopes=["read:requests"],
        is_active=True
    )
    db_session.add(api_key)
    await db_session.commit()

    response = await client.delete(
        f"{settings.API_V1_STR}/api-keys/{api_key.id}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # بررسی غیرفعال شدن کلید
    updated_key = await db_session.get(APIKey, api_key.id)
    assert not updated_key.is_active


@pytest.mark.asyncio
async def test_revoke_api_key_not_found(
    app: FastAPI,
    client: AsyncClient,
    test_user: User
):
    """تست غیرفعال کردن کلید API ناموجود"""
    response = await client.delete(
        f"{settings.API_V1_STR}/api-keys/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_revoke_api_key_unauthorized(
    app: FastAPI,
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User
):
    """تست غیرفعال کردن کلید API توسط کاربر غیرمجاز"""
    # ایجاد کلید API برای کاربر اول
    api_key = APIKey(
        user_id=test_user.id,
        name="Test Key",
        key_hash="test_hash",
        prefix="sk_live_",
        scopes=["read:requests"],
        is_active=True
    )
    db_session.add(api_key)
    await db_session.commit()

    # تلاش برای غیرفعال کردن با کاربر دوم
    response = await client.delete(
        f"{settings.API_V1_STR}/api-keys/{api_key.id}",
        headers={"Authorization": f"Bearer {other_user.token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND  # برای امنیت، همان پیام not found را نمایش می‌دهیم