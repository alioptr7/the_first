"""
Rate Limit Grace Period Middleware
برای اضافه کردن headers و هشدارات به پاسخ‌ها
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from rate_limiter import RateLimiter, LimitLevel
from db.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RateLimitGracePeriodMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling rate limit grace period
    
    - Adds rate limit headers to all responses
    - Checks for 80% warning threshold
    - Handles soft block (110%) with 5-minute grace
    - Enforces hard block (100%)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        بررسی Rate Limit و اضافه کردن headers
        """
        
        # Skip rate limiting برای بعضی endpoints
        if request.url.path in ["/health", "/health/ready", "/health/detailed", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # فقط برای authenticated requests
        user_id = request.headers.get("X-User-ID") or request.headers.get("user_id")
        profile = request.headers.get("X-User-Profile", "free")
        
        if not user_id:
            # ادامه بدون بررسی rate limit
            response = await call_next(request)
            return response
        
        try:
            # بررسی Rate Limit
            redis_client = await get_redis_client()
            rate_limiter = RateLimiter(redis_client.client)
            
            limit_level, details = await rate_limiter.check_limit(user_id, profile)
            
            # ✅ OK - ادامه عادی
            if limit_level == LimitLevel.OK:
                response = await call_next(request)
                
                # اضافه کردن headers
                response.headers["X-RateLimit-Limit-Minute"] = str(details.get("hit_limit", "∞"))
                response.headers["X-RateLimit-Remaining-Minute"] = str(details["remaining_minute"])
                response.headers["X-RateLimit-Remaining-Hour"] = str(details["remaining_hour"])
                response.headers["X-RateLimit-Remaining-Day"] = str(details["remaining_day"])
                
                # Increment counter بعد از پاسخ
                await rate_limiter.increment_counter(user_id)
                
                return response
            
            # ⚠️ WARNING (80%) - اجازه دارد اما هشدار
            elif limit_level == LimitLevel.WARNING:
                # فعال‌سازی soft block برای 5 دقیقه
                await rate_limiter.activate_soft_block(user_id, details.get("hit_limit", "hour"))
                
                response = await call_next(request)
                
                # Add warning headers
                response.headers["X-RateLimit-Status"] = "WARNING"
                response.headers["X-RateLimit-Message"] = details["message"]
                response.headers["X-RateLimit-Remaining-Minute"] = str(details["remaining_minute"])
                response.headers["X-RateLimit-Remaining-Hour"] = str(details["remaining_hour"])
                response.headers["X-RateLimit-Remaining-Day"] = str(details["remaining_day"])
                
                # Increment counter
                await rate_limiter.increment_counter(user_id)
                
                logger.warning(f"User {user_id} reached {details['hit_limit']} warning threshold")
                
                return response
            
            # 🔶 SOFT BLOCK (110%, grace period فعال) - اجازه دارد اما محدود
            elif limit_level == LimitLevel.SOFT_BLOCK:
                response = await call_next(request)
                
                # Add soft block headers
                response.headers["X-RateLimit-Status"] = "SOFT_BLOCK"
                response.headers["X-RateLimit-Message"] = "Soft block active - grace period enabled (5 min)"
                response.headers["X-RateLimit-Grace-Period-Ends"] = details.get("grace_period_ends_at", "")
                response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, details["remaining_minute"]))
                response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, details["remaining_hour"]))
                response.headers["X-RateLimit-Remaining-Day"] = str(max(0, details["remaining_day"]))
                
                # Increment counter
                await rate_limiter.increment_counter(user_id)
                
                logger.warning(f"User {user_id} in soft block grace period for {details['hit_limit']}")
                
                return response
            
            # ❌ EXCEEDED (100%, hard block) - مسدود شود
            elif limit_level == LimitLevel.EXCEEDED:
                logger.warning(f"User {user_id} exceeded rate limit for {details['hit_limit']}")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded for {details['hit_limit']}",
                        "retry_after": 60 if details["hit_limit"] == "minute" else 300,
                        "remaining": {
                            "minute": details["remaining_minute"],
                            "hour": details["remaining_hour"],
                            "day": details["remaining_day"],
                        },
                        "limit_exceeded": details["hit_limit"],
                    },
                    headers={
                        "X-RateLimit-Status": "EXCEEDED",
                        "X-RateLimit-Message": details["message"],
                        "Retry-After": str(60 if details["hit_limit"] == "minute" else 300),
                        "X-RateLimit-Remaining-Minute": str(details["remaining_minute"]),
                        "X-RateLimit-Remaining-Hour": str(details["remaining_hour"]),
                        "X-RateLimit-Remaining-Day": str(details["remaining_day"]),
                    }
                )
            
        except Exception as e:
            logger.error(f"Rate limit middleware error: {e}")
            # در صورت error، ادامه بدهید
            response = await call_next(request)
            return response
        
        # Default: ادامه عادی
        response = await call_next(request)
        return response
