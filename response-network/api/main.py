import logging
import sys
import os
from pathlib import Path

import redis
from fastapi import Depends, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# --- Start of Path Fix ---
# Add project root to the Python path to allow imports from `shared`
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# --- End of Path Fix ---

from core.config import settings
from db.session import get_db_session
from dependencies import get_api_key
from router import auth_router
from router import stats_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Monitoring and Admin API for the isolated Response Network.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include routers
app.include_router(auth_router.router)
app.include_router(stats_router.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Monitoring API startup...")

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Basic liveness check."""
    return {"status": "ok"}

@app.get("/health/detailed", tags=["Monitoring"], dependencies=[Depends(get_api_key)])
async def detailed_health_check(db: AsyncSession = Depends(get_db_session)):
    """
    Performs a detailed health check on critical services.
    """
    health_status = {
        "database": "disconnected",
        "redis_broker": "disconnected",
    }
    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        redis_client = redis.from_url(str(settings.REDIS_URL))
        if redis_client.ping():
            health_status["redis_broker"] = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    return health_status

@app.get("/stats/queues", tags=["Monitoring"], dependencies=[Depends(get_api_key)])
async def queue_stats():
    """
    Gets the length of the main Celery task queues.
    """
    try:
        redis_client = redis.from_url(str(settings.REDIS_URL))
        # Celery's default queue is named 'celery'
        default_queue_length = redis_client.llen("celery")
        # Celery creates other internal queues, we can monitor them too if needed.
        return {
            "default_queue_length": default_queue_length,
            "notes": "This shows pending tasks in the default queue.",
        }
    except Exception as e:
        logger.error(f"Could not get queue stats: {e}")
        raise HTTPException(status_code=500, detail="Could not connect to Redis to get queue stats.")

@app.get("/stats/workers", tags=["Monitoring"], dependencies=[Depends(get_api_key)])
async def worker_stats():
    """
    Gets a list of active (online) Celery workers by pinging them.
    """
    try:
        # The inspect().ping() is a blocking I/O call.
        # For a simple monitoring API with a short timeout, this is acceptable.
        # In a high-load scenario, consider running it in a thread pool.
        inspector = celery_app.control.inspect(timeout=1)
        active_workers = inspector.ping()

        if active_workers is None:
            # This can happen if the broker is down or no workers are connected.
            return {"active_workers": [], "count": 0, "status": "No workers responded. Broker might be down or no workers are running."}

        return {
            "active_workers": list(active_workers.keys()),
            "count": len(active_workers),
        }
    except Exception as e:
        logger.error(f"Could not get worker stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not inspect Celery workers: {e}")

@app.get("/stats/cache", tags=["Monitoring"], dependencies=[Depends(get_api_key)])
async def cache_stats():
    """
    Gets statistics about the Redis cache, including memory usage and hit/miss ratio.
    """
    try:
        # Use decode_responses=True to get strings instead of bytes
        redis_client = redis.from_url(str(settings.REDIS_URL), decode_responses=True)
        info = redis_client.info()

        hits = int(info.get("keyspace_hits", 0))
        misses = int(info.get("keyspace_misses", 0))
        total_lookups = hits + misses

        cache_metrics = {
            "memory": {
                "used_memory_human": info.get("used_memory_human"),
                "peak_memory_human": info.get("used_memory_peak_human"),
                "max_memory_human": info.get("maxmemory_human", "N/A"),
                "fragmentation_ratio": info.get("mem_fragmentation_ratio"),
                "eviction_policy": info.get("maxmemory_policy"),
            },
            "stats": {
                "total_keys": redis_client.dbsize(),
                "keyspace_hits": hits,
                "keyspace_misses": misses,
                "hit_ratio": f"{(hits / total_lookups * 100):.2f}%" if total_lookups > 0 else "N/A",
            },
            "clients": {
                "connected_clients": info.get("connected_clients"),
            },
        }

        return cache_metrics

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Could not connect to Redis for cache stats: {e}")
        raise HTTPException(status_code=503, detail="Could not connect to Redis.")