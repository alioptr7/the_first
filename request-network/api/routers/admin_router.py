from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, case, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_admin
from db.session import get_db_session
from db.redis_client import get_redis_client
from models.user import User
from models.request import Request
from models.batch import ExportBatch, ImportBatch
from schemas.admin import SystemStats
from rate_limiter import RateLimiter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
    # Remove global dependencies - add them per endpoint instead
)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[None, Depends(require_admin)] = None  # Add auth check here
):
    """
    Retrieves overall statistics for the system.
    - User counts (total, active)
    - Request counts by status
    - Batch counts (import/export)
    """
    # 1. Get user stats
    user_stats_stmt = select(
        func.count(User.id).label("total_users"),
        func.count(case((User.is_active, 1))).label("active_users")
    )
    user_stats_result = (await db.execute(user_stats_stmt)).one()

    # 2. Get request stats
    request_stats_stmt = select(
        func.count(Request.id).label("total_requests"),
        func.count(case((Request.status == 'pending', 1))).label("pending_requests"),
        func.count(case((Request.status == 'completed', 1))).label("completed_requests"),
        func.count(case((Request.status == 'failed', 1))).label("failed_requests"),
    )
    request_stats_result = (await db.execute(request_stats_stmt)).one()

    # 3. Get batch stats
    export_batch_count = await db.scalar(select(func.count(ExportBatch.id)))
    import_batch_count = await db.scalar(select(func.count(ImportBatch.id)))

    return SystemStats(
        total_users=user_stats_result.total_users,
        active_users=user_stats_result.active_users,
        total_requests=request_stats_result.total_requests,
        pending_requests=request_stats_result.pending_requests,
        completed_requests=request_stats_result.completed_requests,
        failed_requests=request_stats_result.failed_requests,
        total_export_batches=export_batch_count or 0,
        total_import_batches=import_batch_count or 0,
    )


@router.get("/cache/stats")
async def get_cache_stats(
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Get Redis cache statistics.
    
    Returns:
    - Status (connected/disconnected)
    - Number of cached responses
    - Memory usage
    - Connected clients
    """
    redis_client = await get_redis_client()
    stats = await redis_client.get_cache_stats()
    return stats


@router.delete("/cache/clear")
async def clear_all_cache(
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Clear all cached responses (admin only).
    Use with caution - all cached data will be lost.
    
    Returns:
    - Success message
    - Number of entries cleared
    """
    redis_client = await get_redis_client()
    
    # Get stats before clearing
    stats_before = await redis_client.get_cache_stats()
    cleared_count = stats_before.get("response_cache_keys", 0)
    
    # Clear all cache
    success = await redis_client.clear_all_cache()
    
    return {
        "success": success,
        "message": f"Cache cleared successfully" if success else "Failed to clear cache",
        "entries_cleared": cleared_count
    }


@router.delete("/cache/user/{user_id}")
async def clear_user_cache(
    user_id: str,
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Invalidate all cached responses for a specific user (admin only).
    
    Args:
        user_id: UUID of the user
        
    Returns:
    - Success message
    - Number of entries invalidated
    """
    redis_client = await get_redis_client()
    deleted_count = await redis_client.invalidate_user_cache(user_id)
    
    return {
        "success": True,
        "message": f"User cache invalidated",
        "entries_invalidated": deleted_count,
        "user_id": user_id
    }


# ============================================================================
# RATE LIMITING ENDPOINTS (Grace Period)
# ============================================================================


@router.get("/rate-limit/user/{user_id}/stats")
async def get_user_rate_limit_stats(
    user_id: str,
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Get rate limit statistics for a specific user.
    
    Shows:
    - Current usage (minute, hour, day)
    - Percentage of limit used
    - Reset times
    """
    redis_client = await get_redis_client()
    rate_limiter = RateLimiter(redis_client.client)
    
    # Get user profile from database
    db = next(get_db_session())
    user = await db.get(User, user_id)
    profile = user.profile if user else "free"
    
    stats = await rate_limiter.get_user_stats(user_id, profile)
    return stats


@router.post("/rate-limit/user/{user_id}/reset")
async def reset_user_rate_limit(
    user_id: str,
    window: str = "all",
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Reset rate limit counter for a user (admin only).
    
    Args:
        user_id: UUID of the user
        window: Which window to reset (minute, hour, day, all)
        
    Returns:
    - Success message
    - Number of counters reset
    """
    redis_client = await get_redis_client()
    rate_limiter = RateLimiter(redis_client.client)
    
    result = await rate_limiter.reset_user_limit(user_id, window)
    return result


@router.post("/rate-limit/user/{user_id}/custom-limits")
async def set_custom_rate_limits(
    user_id: str,
    minute: int = None,
    hour: int = None,
    day: int = None,
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Set custom rate limits for a user (admin only).
    
    This overrides the default profile limits.
    
    Args:
        user_id: UUID of the user
        minute: Custom per-minute limit
        hour: Custom per-hour limit
        day: Custom per-day limit
        
    Returns:
    - Success message
    - Applied custom limits
    """
    redis_client = await get_redis_client()
    rate_limiter = RateLimiter(redis_client.client)
    
    result = await rate_limiter.set_custom_limits(user_id, minute, hour, day)
    return result


@router.get("/rate-limit/all")
async def get_all_rate_limits(
    _: Annotated[None, Depends(require_admin)] = None
):
    """
    Get rate limit configuration for all profiles.
    
    Returns:
    - Limits for each profile (free, basic, premium, enterprise)
    - Warning thresholds (80%, 110%)
    - Hard block threshold (100%)
    """
    from rate_limiter import RateLimitConfig
    
    config = RateLimitConfig()
    
    return {
        "limits": config.LIMITS,
        "thresholds": {
            "warning": f"{config.WARNING_THRESHOLD * 100}%",
            "soft_block": f"{config.SOFT_BLOCK_THRESHOLD * 100}%",
            "hard_block": f"{config.HARD_BLOCK_THRESHOLD * 100}%",
        },
        "grace_period_duration": "5 minutes",
        "message": "Grace Period allows soft overflow for 5 minutes before hard block"
    }