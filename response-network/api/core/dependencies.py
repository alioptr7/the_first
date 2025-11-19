from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.session import async_session, SessionLocal
from .config import settings

from redis.asyncio import Redis

async def get_db() -> AsyncSession:
    """Get async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_db_sync() -> Session:
    """Get synchronous database session for Celery tasks."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def get_current_superuser(token: str = None):
    """Get current superuser from token."""
    # This is a placeholder - implement based on your auth logic
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return None

async def get_redis() -> Redis:
    """Get async Redis client for Celery tasks."""
    redis_url = str(settings.REDIS_URL)
    redis = await Redis.from_url(redis_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

