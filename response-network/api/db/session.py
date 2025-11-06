from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_CONNECTION_URL),
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging SQL queries
)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()