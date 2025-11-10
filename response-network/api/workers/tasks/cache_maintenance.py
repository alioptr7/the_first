from datetime import datetime, timedelta
import asyncio

from celery import shared_task
from sqlalchemy import select, delete

from core.config import settings
from core.dependencies import get_db, get_redis
from models.request import Request
from models.cache import Cache

@shared_task
def cleanup_old_cache():
    """Clean up expired cache entries."""
    async def _cleanup():
        async with get_db() as db:
            # Delete expired cache entries
            expire_before = datetime.utcnow() - timedelta(days=settings.CACHE_TTL_DAYS)
            result = await db.execute(
                delete(Cache)
                .where(Cache.created_at < expire_before)
                .returning(Cache.id)
            )
            deleted_ids = result.scalars().all()
            await db.commit()
            
            return f"Deleted {len(deleted_ids)} expired cache entries"
    
    return asyncio.run(_cleanup())

@shared_task
def cleanup_redis_cache():
    """Clean up expired Redis cache entries."""
    async def _cleanup():
        redis = await get_redis()
        # Get all keys matching our pattern
        pattern = "cache:*"
        keys = await redis.keys(pattern)
        
        deleted = 0
        for key in keys:
            ttl = await redis.ttl(key)
            if ttl < 0:  # No TTL set or expired
                await redis.delete(key)
                deleted += 1
        
        return f"Deleted {deleted} expired Redis cache entries"
    
    return asyncio.run(_cleanup())