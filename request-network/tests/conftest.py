import asyncio
from typing import AsyncGenerator, Generator
from datetime import timedelta

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import settings
from api.db.session import get_db
from api.main import app as main_app
from api.models.user import User
from api.auth.security import create_access_token, get_password_hash
from api.db.base_class import Base

# Create a new asynchronous engine for the test database
engine = create_async_engine(settings.TEST_DATABASE_URI, echo=True)

# Create a new sessionmaker for the test database
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Creates an instance of the default event loop for each test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Create the database schema before running tests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    """
    Fixture to provide the FastAPI app.
    """
    yield main_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to provide an async test client.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to provide a database session.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Fixture to create a test user.
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """
    Fixture to create another test user.
    """
    user = User(
        username="otheruser",
        email="otheruser@example.com",
        hashed_password=get_password_hash("otherpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """
    Fixture to create an admin user.
    """
    user = User(
        username="adminuser",
        email="adminuser@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user: User) -> dict[str, str]:
    """
    Fixture to provide an admin user's token.
    """
    token = create_access_token(
        data={"sub": admin_user.email}, expires_delta=timedelta(minutes=15)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_admin_token(admin_user: User) -> dict[str, str]:
    """
    Fixture to provide an expired admin user's token.
    """
    token = create_access_token(
        data={"sub": admin_user.email}, expires_delta=timedelta(minutes=-1)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def non_admin_token(test_user: User) -> dict[str, str]:
    """
    Fixture to provide a non-admin user's token.
    """
    token = create_access_token(
        data={"sub": test_user.email}, expires_delta=timedelta(minutes=15)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_token(test_user: User) -> dict[str, str]:
    """
    Fixture to provide a test user's token.
    """
    token = create_access_token(
        data={"sub": test_user.email}, expires_delta=timedelta(minutes=15)
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_token(other_user: User) -> dict[str, str]:
    """
    Fixture to provide another test user's token.
    """
    token = create_access_token(
        data={"sub": other_user.email}, expires_delta=timedelta(minutes=15)
    )
    return {"Authorization": f"Bearer {token}"}
