import logging

from workers.celery_app import celery_app
from workers.redis_client import get_redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.cache_maintenance.maintain_cache")
def maintain_cache():
    """
    Performs cache maintenance tasks, primarily focusing on monitoring and logging.
    - Logs Redis memory usage.
    - Logs the number of keys in the cache.
    Note: Redis handles TTL expiration automatically. This task is for observation.
    """
    logger.info("Starting cache maintenance task...")
    redis_client = get_redis_client()

    try:
        # Get memory usage info
        info = redis_client.info('memory')
        used_memory_human = info.get('used_memory_human', 'N/A')
        max_memory_human = info.get('maxmemory_human', 'N/A')
        
        logger.info(
            f"Redis Cache Stats - Memory Usage: {used_memory_human} / {max_memory_human}"
        )

        # Get number of keys. Note: Can be slow on very large databases.
        db_size = redis_client.dbsize()
        logger.info(f"Redis Cache Stats - Total Keys: {db_size}")

        return f"Cache maintenance check completed. Memory: {used_memory_human}, Keys: {db_size}"
    except Exception as e:
        logger.error(f"Cache maintenance task failed: {e}", exc_info=True)
        raise