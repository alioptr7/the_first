import logging

from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.redis_client import get_redis_client
from workers.elasticsearch_client import ElasticsearchClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(
    name="workers.tasks.system_monitoring.system_health_check",
    bind=True,
    max_retries=0  # We don't want to retry health checks
)
async def system_health_check(self):
    """
    Performs a health check on critical services (PostgreSQL, Redis, Elasticsearch)
    and logs the status.
    """
    logger.info("Starting system health check task...")
    health_status = {
        "postgresql": "UNKNOWN",
        "redis": "UNKNOWN",
        "elasticsearch": "UNKNOWN",
    }

    # 1. Check PostgreSQL
    try:
        with db_session_scope() as db:
            db.execute("SELECT 1")
        health_status["postgresql"] = "OK"
    except Exception as e:
        health_status["postgresql"] = f"FAIL: {e}"
        logger.error("Health Check Failed: PostgreSQL connection error.", exc_info=True)

    # 2. Check Redis
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["redis"] = "OK"
    except Exception as e:
        health_status["redis"] = f"FAIL: {e}"
        logger.error("Health Check Failed: Redis connection error.", exc_info=True)

    # 3. Check Elasticsearch
    es_client = ElasticsearchClient()
    try:
        if await es_client.check_health():
            health_status["elasticsearch"] = "OK"
        else:
            health_status["elasticsearch"] = "FAIL: Unhealthy status reported."
            logger.warning("Health Check: Elasticsearch cluster is unhealthy.")
    finally:
        await es_client.close_connection()

    logger.info(f"System Health Check Report: {health_status}")
    return health_status