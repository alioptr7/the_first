"""
Rate Limiter with Grace Period Support
فرهنگ پیاده‌سازی: Fixed Window algorithm با محدودیت چندگانه
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from enum import Enum

from redis.asyncio import Redis
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class LimitLevel(str, Enum):
    """سطح‌های محدودیت برای Rate Limiting"""
    OK = "ok"  # ✅ در حد معمولی است
    WARNING = "warning"  # ⚠️ 80% استفاده شده (Grace Period)
    EXCEEDED = "exceeded"  # ❌ 100% استفاده شده (Hard Block)
    SOFT_BLOCK = "soft_block"  # 🔶 110% - اجازه دارد اما هشدار


class RateLimitConfig:
    """تنظیمات Rate Limiting برای پروفایل‌های کاربری"""

    # Default limits (per profile)
    LIMITS = {
        "free": {
            "minute": 10,
            "hour": 100,
            "day": 1000,
        },
        "basic": {
            "minute": 30,
            "hour": 500,
            "day": 5000,
        },
        "premium": {
            "minute": 100,
            "hour": 2000,
            "day": 20000,
        },
        "enterprise": {
            "minute": 500,
            "hour": 10000,
            "day": 100000,
        },
    }

    # Grace Period Thresholds
    WARNING_THRESHOLD = 0.80  # 80% - شروع هشدار
    SOFT_BLOCK_THRESHOLD = 1.10  # 110% - اجازه دارد اما به مدت محدود
    HARD_BLOCK_THRESHOLD = 1.0  # 100% - مسدود شود


class RateLimiter:
    """
    Rate Limiter with Grace Period Support
    
    Features:
    - Fixed Window algorithm (minute, hour, day windows)
    - Grace Period (80% warning, 110% soft block for 5 min, 100% hard block)
    - Per-user limits based on profile
    - Redis-based counter storage
    - Admin reset capability
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.config = RateLimitConfig()

    async def get_user_limits(self, user_id: str, profile: str = "free") -> Dict:
        """
        دریافت محدودیت‌های کاربر بر اساس پروفایل
        
        Args:
            user_id: ID کاربر
            profile: نوع پروفایل (free, basic, premium, enterprise)
            
        Returns:
            محدودیت‌های دقیق کاربر
        """
        limits = self.config.LIMITS.get(profile, self.config.LIMITS["free"])
        
        # بررسی override توسط ادمین
        custom_key = f"rate_limit:custom:{user_id}"
        custom_limits = await self.redis.hgetall(custom_key)
        
        if custom_limits:
            limits = {
                "minute": int(custom_limits.get(b"minute", limits["minute"])),
                "hour": int(custom_limits.get(b"hour", limits["hour"])),
                "day": int(custom_limits.get(b"day", limits["day"])),
            }
        
        return limits

    def _get_window_keys(self, user_id: str) -> Dict[str, str]:
        """
        Generate Redis keys برای windows مختلف
        
        Returns:
            Dict با keys برای minute, hour, day windows
        """
        now = datetime.utcnow()
        
        return {
            "minute": f"rate_limit:{user_id}:minute:{now.strftime('%Y%m%d%H%M')}",
            "hour": f"rate_limit:{user_id}:hour:{now.strftime('%Y%m%d%H')}",
            "day": f"rate_limit:{user_id}:day:{now.strftime('%Y%m%d')}",
        }

    async def check_limit(
        self, user_id: str, profile: str = "free"
    ) -> Tuple[LimitLevel, Dict]:
        """
        بررسی Rate Limit با Grace Period Support
        
        Returns:
            Tuple[LimitLevel, details_dict]
            
        Details Dict شامل:
            - remaining_minute, remaining_hour, remaining_day
            - reset_at_minute, reset_at_hour, reset_at_day
            - hit_limit (کدام limit ایجاد هشدار می‌کند)
            - message: توضیح انگلیسی
        """
        try:
            limits = await self.get_user_limits(user_id, profile)
            keys = self._get_window_keys(user_id)
            
            # دریافت شمارنده‌های فعلی
            counts = {
                "minute": int(await self.redis.get(keys["minute"]) or 0),
                "hour": int(await self.redis.get(keys["hour"]) or 0),
                "day": int(await self.redis.get(keys["day"]) or 0),
            }
            
            # محاسبه استفاده (0-1 scale)
            usage = {
                "minute": counts["minute"] / limits["minute"],
                "hour": counts["hour"] / limits["hour"],
                "day": counts["day"] / limits["day"],
            }
            
            # بررسی سطح محدودیت
            # 1. Hard Block (100% exceeded)
            for window in ["minute", "hour", "day"]:
                if counts[window] >= limits[window]:
                    return LimitLevel.EXCEEDED, {
                        "remaining_minute": max(0, limits["minute"] - counts["minute"]),
                        "remaining_hour": max(0, limits["hour"] - counts["hour"]),
                        "remaining_day": max(0, limits["day"] - counts["day"]),
                        "hit_limit": window,
                        "message": f"Rate limit exceeded for {window}",
                        "usage": usage,
                    }
            
            # 2. Soft Block (80-100%, تا 5 دقیقه grace period)
            for window in ["minute", "hour", "day"]:
                if usage[window] >= self.config.WARNING_THRESHOLD:
                    # Check if soft block is active
                    soft_block_key = f"rate_limit:soft_block:{user_id}:{window}"
                    soft_block_active = await self.redis.exists(soft_block_key)
                    
                    if soft_block_active:
                        return LimitLevel.SOFT_BLOCK, {
                            "remaining_minute": max(0, limits["minute"] - counts["minute"]),
                            "remaining_hour": max(0, limits["hour"] - counts["hour"]),
                            "remaining_day": max(0, limits["day"] - counts["day"]),
                            "hit_limit": window,
                            "message": f"Soft block active for {window} (grace period)",
                            "usage": usage,
                            "grace_period_ends_at": (
                                datetime.utcnow() + timedelta(minutes=5)
                            ).isoformat(),
                        }
                    
                    return LimitLevel.WARNING, {
                        "remaining_minute": max(0, limits["minute"] - counts["minute"]),
                        "remaining_hour": max(0, limits["hour"] - counts["hour"]),
                        "remaining_day": max(0, limits["day"] - counts["day"]),
                        "hit_limit": window,
                        "message": f"Approaching {window} limit (80% used)",
                        "usage": usage,
                    }
            
            # 3. OK - کمتر از 80%
            return LimitLevel.OK, {
                "remaining_minute": limits["minute"] - counts["minute"],
                "remaining_hour": limits["hour"] - counts["hour"],
                "remaining_day": limits["day"] - counts["day"],
                "hit_limit": None,
                "message": "Rate limit OK",
                "usage": usage,
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit for user {user_id}: {e}")
            # اگر Redis خراب باشد، اجازه بدهید
            return LimitLevel.OK, {"message": "Rate limit check failed (Redis error)"}

    async def increment_counter(self, user_id: str) -> None:
        """
        Increment شمارنده‌های Rate Limit
        
        تمام 3 window را increment می‌کند (minute, hour, day)
        """
        try:
            keys = self._get_window_keys(user_id)
            
            # Increment همه keys با TTL
            pipeline = self.redis.pipeline()
            
            # Minute window (60 ثانیه)
            pipeline.incr(keys["minute"])
            pipeline.expire(keys["minute"], 60)
            
            # Hour window (3600 ثانیه)
            pipeline.incr(keys["hour"])
            pipeline.expire(keys["hour"], 3600)
            
            # Day window (86400 ثانیه)
            pipeline.incr(keys["day"])
            pipeline.expire(keys["day"], 86400)
            
            await pipeline.execute()
            
        except Exception as e:
            logger.warning(f"Error incrementing counter for user {user_id}: {e}")

    async def activate_soft_block(self, user_id: str, window: str = "hour") -> None:
        """
        Grace Period فعال‌سازی برای 5 دقیقه
        
        در این مدت کاربر می‌تواند درخواست بدهد اما با هشدار
        """
        try:
            soft_block_key = f"rate_limit:soft_block:{user_id}:{window}"
            await self.redis.setex(soft_block_key, 300, "1")  # 5 minutes
            logger.info(f"Soft block activated for user {user_id} on {window}")
        except Exception as e:
            logger.error(f"Error activating soft block for user {user_id}: {e}")

    async def reset_user_limit(self, user_id: str, window: str = "all") -> Dict:
        """
        Reset محدودیت کاربر (Admin operation)
        
        Args:
            user_id: ID کاربر
            window: کدام window را reset کند (minute, hour, day, all)
            
        Returns:
            تعداد counters که reset شدند
        """
        try:
            keys = self._get_window_keys(user_id)
            reset_count = 0
            
            if window == "all":
                windows = ["minute", "hour", "day"]
            else:
                windows = [window]
            
            pipeline = self.redis.pipeline()
            
            for w in windows:
                if w in keys:
                    pipeline.delete(keys[w])
                    reset_count += 1
            
            await pipeline.execute()
            logger.info(f"Rate limit reset for user {user_id}: {window}")
            
            return {
                "user_id": user_id,
                "window": window,
                "reset_count": reset_count,
                "message": f"Rate limit reset for {window}",
            }
            
        except Exception as e:
            logger.error(f"Error resetting rate limit for user {user_id}: {e}")
            return {"error": str(e)}

    async def set_custom_limits(
        self, user_id: str, minute: int = None, hour: int = None, day: int = None
    ) -> Dict:
        """
        تنظیم محدودیت‌های Custom برای کاربر (Admin operation)
        
        Args:
            user_id: ID کاربر
            minute/hour/day: محدودیت‌های جدید (None = عدم تغییر)
        """
        try:
            custom_key = f"rate_limit:custom:{user_id}"
            
            if minute or hour or day:
                data = {}
                if minute:
                    data["minute"] = minute
                if hour:
                    data["hour"] = hour
                if day:
                    data["day"] = day
                
                await self.redis.hset(custom_key, mapping=data)
                logger.info(f"Custom limits set for user {user_id}: {data}")
                
                return {"user_id": user_id, "custom_limits": data}
            
            return {"error": "No limits provided"}
            
        except Exception as e:
            logger.error(f"Error setting custom limits for user {user_id}: {e}")
            return {"error": str(e)}

    async def get_user_stats(self, user_id: str, profile: str = "free") -> Dict:
        """
        دریافت آمار کامل کاربر برای Admin Panel
        
        شامل:
        - فعلی usage برای هر window
        - نسبت به محدودیت
        - زمان reset
        """
        try:
            limits = await self.get_user_limits(user_id, profile)
            keys = self._get_window_keys(user_id)
            
            counts = {
                "minute": int(await self.redis.get(keys["minute"]) or 0),
                "hour": int(await self.redis.get(keys["hour"]) or 0),
                "day": int(await self.redis.get(keys["day"]) or 0),
            }
            
            now = datetime.utcnow()
            
            return {
                "user_id": user_id,
                "profile": profile,
                "limits": limits,
                "usage": counts,
                "percentages": {
                    "minute": round((counts["minute"] / limits["minute"]) * 100, 2),
                    "hour": round((counts["hour"] / limits["hour"]) * 100, 2),
                    "day": round((counts["day"] / limits["day"]) * 100, 2),
                },
                "reset_at": {
                    "minute": (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    "hour": (now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    "day": (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                },
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return {"error": str(e)}
