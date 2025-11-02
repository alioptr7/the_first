from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

# ایجاد یک موتور دیتابیس غیرهمزمان
# pool_pre_ping=True: قبل از هر استفاده، اتصال را چک می‌کند تا از اتصالات مرده جلوگیری شود.
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,  # در محیط تست، لاگ‌های SQL را غیرفعال می‌کنیم
    pool_pre_ping=True,
)

# ایجاد یک کارخانه برای ساخت session های غیرهمزمان
AsyncSessionFactory = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.
    Ensures the session is always closed after the request.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()