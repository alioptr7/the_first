"""
Rate limiter for user requests
"""
import redis
from datetime import datetime, timedelta
from typing import Tuple, Optional
from models.user import User
from core.config import settings


class RateLimiter:
    """
    Rate limiter for user requests using Redis.
    
    Supports three levels:
    - Per minute
    - Per hour
    - Per day
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection for rate limiting"""
        if redis_url is None:
            redis_url = str(settings.REDIS_URL)
        self.redis = redis.from_url(redis_url)
    
    def _get_key(self, user_id: str, period: str) -> str:
        """Generate Redis key for storing request count"""
        now = datetime.utcnow()
        
        if period == "minute":
            time_key = now.strftime("%Y%m%d%H%M")  # YYYYMMDDHHMM
        elif period == "hour":
            time_key = now.strftime("%Y%m%d%H")    # YYYYMMDDHH
        elif period == "day":
            time_key = now.strftime("%Y%m%d")      # YYYYMMDD
        else:
            raise ValueError(f"Unknown period: {period}")
        
        return f"rate_limit:{user_id}:{period}:{time_key}"
    
    def _get_ttl(self, period: str) -> int:
        """Get TTL (time to live) in seconds for Redis key"""
        if period == "minute":
            return 70  # 60 seconds + buffer
        elif period == "hour":
            return 3700  # 1 hour + buffer
        elif period == "day":
            return 86500  # 24 hours + buffer
        else:
            raise ValueError(f"Unknown period: {period}")
    
    def check_rate_limit(self, user: User) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits.
        
        Returns:
            (is_allowed: bool, message: str)
            - (True, "OK") if allowed
            - (False, error_message) if exceeded
        """
        # Check per-minute limit
        minute_key = self._get_key(str(user.id), "minute")
        minute_count = self.redis.incr(minute_key)
        if minute_count == 1:
            self.redis.expire(minute_key, self._get_ttl("minute"))
        
        if minute_count > user.rate_limit_per_minute:
            return False, f"Rate limit exceeded (per minute): {minute_count}/{user.rate_limit_per_minute}"
        
        # Check per-hour limit
        hour_key = self._get_key(str(user.id), "hour")
        hour_count = self.redis.incr(hour_key)
        if hour_count == 1:
            self.redis.expire(hour_key, self._get_ttl("hour"))
        
        if hour_count > user.rate_limit_per_hour:
            return False, f"Rate limit exceeded (per hour): {hour_count}/{user.rate_limit_per_hour}"
        
        # Check per-day limit
        day_key = self._get_key(str(user.id), "day")
        day_count = self.redis.incr(day_key)
        if day_count == 1:
            self.redis.expire(day_key, self._get_ttl("day"))
        
        if day_count > user.rate_limit_per_day:
            return False, f"Rate limit exceeded (per day): {day_count}/{user.rate_limit_per_day}"
        
        return True, "OK"
    
    def get_remaining(self, user: User) -> dict:
        """
        Get remaining requests for each period.
        """
        minute_key = self._get_key(str(user.id), "minute")
        hour_key = self._get_key(str(user.id), "hour")
        day_key = self._get_key(str(user.id), "day")
        
        minute_count = int(self.redis.get(minute_key) or 0)
        hour_count = int(self.redis.get(hour_key) or 0)
        day_count = int(self.redis.get(day_key) or 0)
        
        return {
            "minute": {
                "remaining": max(0, user.rate_limit_per_minute - minute_count),
                "used": minute_count,
                "limit": user.rate_limit_per_minute
            },
            "hour": {
                "remaining": max(0, user.rate_limit_per_hour - hour_count),
                "used": hour_count,
                "limit": user.rate_limit_per_hour
            },
            "day": {
                "remaining": max(0, user.rate_limit_per_day - day_count),
                "used": day_count,
                "limit": user.rate_limit_per_day
            }
        }
    
    def reset_user_limits(self, user_id: str) -> bool:
        """Reset all limits for a user (admin only)"""
        keys = self.redis.keys(f"rate_limit:{user_id}:*")
        if keys:
            self.redis.delete(*keys)
            return True
        return False
