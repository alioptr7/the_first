import redis
from .config import settings

# Create a Redis connection pool
redis_pool = redis.ConnectionPool.from_url(str(settings.REDIS_URL), decode_responses=True)

def get_redis_client():
    """
    Returns a Redis client from the connection pool.
    """
    return redis.Redis(connection_pool=redis_pool)