"""
Redis client for caching responses and managing cache operations.
"""
import json
import logging
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client for caching operations."""
    
    def __init__(self, redis_url: str):
        """Initialize Redis client."""
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self._is_connected = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Test connection
            await self.client.ping()
            self._is_connected = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self._is_connected = False
            logger.info("Redis disconnected")
    
    async def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception:
            return False
    
    async def get_response(self, request_id: str) -> Optional[dict]:
        """
        Get cached response for a request.
        
        Args:
            request_id: UUID of the request
            
        Returns:
            Response data dict or None if not cached
        """
        if not await self.is_connected():
            logger.warning("Redis not connected, skipping cache get")
            return None
        
        try:
            cache_key = self._make_key(request_id)
            cached_value = await self.client.get(cache_key)
            
            if cached_value:
                logger.info(f"✅ Cache HIT for request {request_id}")
                return json.loads(cached_value)
            else:
                logger.info(f"❌ Cache MISS for request {request_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting response from cache: {e}")
            return None
    
    async def set_response(
        self,
        request_id: str,
        response_data: dict,
        ttl_hours: int = 24
    ) -> bool:
        """
        Cache a response for a request.
        
        Args:
            request_id: UUID of the request
            response_data: Response data to cache
            ttl_hours: Time-to-live in hours (default: 24)
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not await self.is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            cache_key = self._make_key(request_id)
            ttl = timedelta(hours=ttl_hours)
            
            await self.client.setex(
                cache_key,
                ttl,
                json.dumps(response_data)
            )
            logger.info(f"✅ Cached response for request {request_id} (TTL: {ttl_hours}h)")
            return True
        except Exception as e:
            logger.error(f"Error setting response in cache: {e}")
            return False
    
    async def invalidate_response(self, request_id: str) -> bool:
        """
        Invalidate/remove cached response.
        
        Args:
            request_id: UUID of the request
            
        Returns:
            True if invalidated, False otherwise
        """
        if not await self.is_connected():
            logger.warning("Redis not connected, skipping cache invalidation")
            return False
        
        try:
            cache_key = self._make_key(request_id)
            deleted = await self.client.delete(cache_key)
            if deleted:
                logger.info(f"✅ Invalidated cache for request {request_id}")
            return bool(deleted)
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """
        Invalidate all cached responses for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of keys deleted
        """
        if not await self.is_connected():
            logger.warning("Redis not connected, skipping user cache invalidation")
            return 0
        
        try:
            pattern = f"response:{user_id}:*"
            keys = await self.client.keys(pattern)
            
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"✅ Invalidated {deleted} cache entries for user {user_id}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
            return 0
    
    async def clear_all_cache(self) -> bool:
        """
        Clear all response cache (use with caution).
        
        Returns:
            True if successful, False otherwise
        """
        if not await self.is_connected():
            logger.warning("Redis not connected, skipping clear all")
            return False
        
        try:
            pattern = "response:*"
            keys = await self.client.keys(pattern)
            
            if keys:
                await self.client.delete(*keys)
                logger.info(f"✅ Cleared {len(keys)} cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return False
    
    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not await self.is_connected():
            logger.warning("Redis not connected")
            return {"status": "disconnected"}
        
        try:
            info = await self.client.info()
            keys = await self.client.keys("response:*")
            
            return {
                "status": "connected",
                "total_keys": info.get("db0", {}).get("keys", 0),
                "response_cache_keys": len(keys),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def _make_key(request_id: str) -> str:
        """Generate cache key for request."""
        return f"response:{request_id}"


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get Redis client (initialize if needed)."""
    global _redis_client
    if _redis_client is None:
        from core.config import settings
        _redis_client = RedisClient(str(settings.REDIS_URL))
        await _redis_client.connect()
    return _redis_client


async def close_redis_client():
    """Close Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
