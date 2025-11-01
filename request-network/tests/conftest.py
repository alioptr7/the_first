"""فیکسچرهای مورد نیاز برای تست‌ها"""
import asyncio
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from api.core.config import settings
from api.db.base import Base
from api.db.session import get_session
from api.models.user import User
from api.main import app

# ایجاد موتور دیتابیس تست
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    poolclass=NullPool,
)
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """ایجاد event loop برای تست‌های async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """فیکسچر جلسه دیتابیس تست"""
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.rollback()
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """فیکسچر کلاینت تست"""
    async def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession) -> User:
    """فیکسچر کاربر ادمین"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password="test_hash",
        is_admin=True
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def normal_user(session: AsyncSession) -> User:
    """فیکسچر کاربر عادی"""
    user = User(
        username="user",
        email="user@example.com",
        hashed_password="test_hash",
        is_admin=False
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def normal_user_token(normal_user: User) -> Dict[str, str]:
    """فیکسچر توکن کاربر عادی"""
    return {"Authorization": f"Bearer {normal_user.generate_token()}"}