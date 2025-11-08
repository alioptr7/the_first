from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session

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