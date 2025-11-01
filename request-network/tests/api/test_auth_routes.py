"""تست‌های مربوط به API‌های احراز هویت"""
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User
from api.core.config import settings


@pytest.mark.asyncio
async def test_login_success(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست موفق ورود کاربر"""
    login_data = {
        "username": test_user.username,
        "password": "test_password",  # باید با رمز عبور در فیکسچر test_user یکسان باشد
        "scopes": ["read:requests", "write:requests"]
    }

    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data  # از data به جای json استفاده می‌کنیم چون OAuth2PasswordRequestForm از form-data استفاده می‌کند
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_invalid_username(
    app: FastAPI,
    client: AsyncClient
):
    """تست ورود با نام کاربری نامعتبر"""
    login_data = {
        "username": "nonexistent_user",
        "password": "test_password",
        "scopes": []
    }

    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست ورود با رمز عبور نامعتبر"""
    login_data = {
        "username": test_user.username,
        "password": "wrong_password",
        "scopes": []
    }

    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_inactive_user(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست ورود با کاربر غیرفعال"""
    # غیرفعال کردن کاربر
    test_user.is_active = False
    session.add(test_user)
    await session.commit()

    login_data = {
        "username": test_user.username,
        "password": "test_password",
        "scopes": []
    }

    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_scopes(
    app: FastAPI,
    client: AsyncClient,
    session: AsyncSession,
    test_user: User
):
    """تست ورود با اسکوپ‌های مختلف"""
    login_data = {
        "username": test_user.username,
        "password": "test_password",
        "scopes": ["read:requests", "write:requests", "admin"]
    }

    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

    # می‌توانیم توکن را decode کنیم و اسکوپ‌ها را بررسی کنیم
    # اما این کار در تست‌های یکپارچگی انجام می‌شود