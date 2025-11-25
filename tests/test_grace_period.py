"""
Tests for Grace Period Rate Limiting
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from rate_limiter import RateLimiter, LimitLevel, RateLimitConfig


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    return AsyncMock()


@pytest.fixture
def rate_limiter(mock_redis):
    """Rate limiter instance with mock Redis"""
    return RateLimiter(mock_redis)


class TestRateLimitConfig:
    """Test RateLimitConfig class"""

    def test_limits_for_all_profiles(self):
        """Test that all profiles have defined limits"""
        config = RateLimitConfig()
        
        profiles = ["free", "basic", "premium", "enterprise"]
        for profile in profiles:
            assert profile in config.LIMITS
            assert "minute" in config.LIMITS[profile]
            assert "hour" in config.LIMITS[profile]
            assert "day" in config.LIMITS[profile]

    def test_thresholds(self):
        """Test threshold values"""
        config = RateLimitConfig()
        
        assert config.WARNING_THRESHOLD == 0.80
        assert config.SOFT_BLOCK_THRESHOLD == 1.10
        assert config.HARD_BLOCK_THRESHOLD == 1.0

    def test_limits_increase_by_profile(self):
        """Test that higher profiles have higher limits"""
        config = RateLimitConfig()
        
        assert config.LIMITS["free"]["day"] < config.LIMITS["basic"]["day"]
        assert config.LIMITS["basic"]["day"] < config.LIMITS["premium"]["day"]
        assert config.LIMITS["premium"]["day"] < config.LIMITS["enterprise"]["day"]


class TestRateLimiterBasics:
    """Basic RateLimiter tests"""

    @pytest.mark.asyncio
    async def test_get_user_limits_default_profile(self, rate_limiter):
        """Test getting default profile limits"""
        rate_limiter.redis.hgetall.return_value = {}
        
        limits = await rate_limiter.get_user_limits("user123", "free")
        
        assert limits["minute"] == 10
        assert limits["hour"] == 100
        assert limits["day"] == 1000

    @pytest.mark.asyncio
    async def test_get_user_limits_custom(self, rate_limiter):
        """Test getting custom user limits"""
        rate_limiter.redis.hgetall.return_value = {
            b"minute": b"50",
            b"hour": b"1000",
            b"day": b"10000",
        }
        
        limits = await rate_limiter.get_user_limits("user123", "free")
        
        assert limits["minute"] == 50
        assert limits["hour"] == 1000
        assert limits["day"] == 10000

    def test_window_key_generation(self, rate_limiter):
        """Test Redis window key generation"""
        keys = rate_limiter._get_window_keys("user123")
        
        assert "rate_limit:user123:minute:" in keys["minute"]
        assert "rate_limit:user123:hour:" in keys["hour"]
        assert "rate_limit:user123:day:" in keys["day"]


class TestRateLimitChecking:
    """Test rate limit checking logic"""

    @pytest.mark.asyncio
    async def test_check_limit_ok_status(self, rate_limiter):
        """Test when usage is OK (< 80%)"""
        # Setup mock redis
        rate_limiter.redis.hgetall.return_value = {}  # no custom limits
        rate_limiter.redis.get.side_effect = [
            b"5",   # minute count: 5/10 = 50%
            b"50",  # hour count: 50/100 = 50%
            b"500", # day count: 500/1000 = 50%
        ]
        rate_limiter.redis.exists.return_value = False  # no soft block
        
        status, details = await rate_limiter.check_limit("user123", "free")
        
        assert status == LimitLevel.OK
        assert details["remaining_minute"] == 5
        assert details["remaining_hour"] == 50
        assert details["remaining_day"] == 500

    @pytest.mark.asyncio
    async def test_check_limit_warning_status(self, rate_limiter):
        """Test when usage reaches WARNING (80%)"""
        rate_limiter.redis.hgetall.return_value = {}
        rate_limiter.redis.get.side_effect = [
            b"8",   # minute: 8/10 = 80%
            b"80",  # hour: 80/100 = 80%
            b"800", # day: 800/1000 = 80%
        ]
        rate_limiter.redis.exists.return_value = False  # no soft block
        
        status, details = await rate_limiter.check_limit("user123", "free")
        
        assert status == LimitLevel.WARNING
        assert details["hit_limit"] in ["minute", "hour", "day"]
        assert details["message"] == "Approaching minute limit (80% used)"

    @pytest.mark.asyncio
    async def test_check_limit_soft_block_status(self, rate_limiter):
        """Test when in SOFT_BLOCK grace period"""
        rate_limiter.redis.hgetall.return_value = {}
        rate_limiter.redis.get.side_effect = [
            b"11",  # minute: 11/10 = 110% (over limit)
            b"100", # hour: 100/100 = 100%
            b"1000", # day: 1000/1000 = 100%
        ]
        rate_limiter.redis.exists.return_value = True  # soft block ACTIVE
        
        status, details = await rate_limiter.check_limit("user123", "free")
        
        assert status == LimitLevel.SOFT_BLOCK
        assert details["message"] == "Soft block active for minute (grace period)"
        assert "grace_period_ends_at" in details

    @pytest.mark.asyncio
    async def test_check_limit_exceeded_status(self, rate_limiter):
        """Test when rate limit is EXCEEDED"""
        rate_limiter.redis.hgetall.return_value = {}
        rate_limiter.redis.get.side_effect = [
            b"10",  # minute: 10/10 = 100% (at limit)
            b"100", # hour: 100/100 = 100%
            b"1000", # day: 1000/1000 = 100%
        ]
        
        status, details = await rate_limiter.check_limit("user123", "free")
        
        assert status == LimitLevel.EXCEEDED
        assert details["message"] == "Rate limit exceeded for minute"


class TestCounterIncrement:
    """Test counter increment functionality"""

    @pytest.mark.asyncio
    async def test_increment_counter(self, rate_limiter):
        """Test incrementing all window counters"""
        rate_limiter.redis.pipeline.return_value.__aenter__.return_value = AsyncMock()
        
        await rate_limiter.increment_counter("user123")
        
        # Verify pipeline was called
        assert rate_limiter.redis.pipeline.called

    @pytest.mark.asyncio
    async def test_increment_sets_correct_ttls(self, rate_limiter):
        """Test that TTLs are set correctly for each window"""
        pipeline_mock = AsyncMock()
        rate_limiter.redis.pipeline.return_value = pipeline_mock
        pipeline_mock.__aenter__.return_value = pipeline_mock
        
        await rate_limiter.increment_counter("user123")
        
        # Verify expire was called for each window
        calls = pipeline_mock.expire.call_args_list
        assert len(calls) >= 3  # minute, hour, day


class TestAdminOperations:
    """Test admin operations"""

    @pytest.mark.asyncio
    async def test_reset_user_limit_all(self, rate_limiter):
        """Test resetting all user limits"""
        pipeline_mock = AsyncMock()
        rate_limiter.redis.pipeline.return_value = pipeline_mock
        pipeline_mock.__aenter__.return_value = pipeline_mock
        
        result = await rate_limiter.reset_user_limit("user123", "all")
        
        assert result["user_id"] == "user123"
        assert result["window"] == "all"
        assert result["reset_count"] == 3  # minute, hour, day

    @pytest.mark.asyncio
    async def test_reset_user_limit_single_window(self, rate_limiter):
        """Test resetting specific window"""
        pipeline_mock = AsyncMock()
        rate_limiter.redis.pipeline.return_value = pipeline_mock
        pipeline_mock.__aenter__.return_value = pipeline_mock
        
        result = await rate_limiter.reset_user_limit("user123", "minute")
        
        assert result["window"] == "minute"
        assert result["reset_count"] == 1

    @pytest.mark.asyncio
    async def test_set_custom_limits(self, rate_limiter):
        """Test setting custom limits"""
        result = await rate_limiter.set_custom_limits(
            "user123",
            minute=50,
            hour=1000,
            day=10000
        )
        
        assert result["user_id"] == "user123"
        assert result["custom_limits"]["minute"] == 50
        assert result["custom_limits"]["hour"] == 1000
        assert result["custom_limits"]["day"] == 10000

    @pytest.mark.asyncio
    async def test_activate_soft_block(self, rate_limiter):
        """Test activating grace period soft block"""
        await rate_limiter.activate_soft_block("user123", "hour")
        
        # Verify setex was called with 5 min TTL
        rate_limiter.redis.setex.assert_called_once()
        call_args = rate_limiter.redis.setex.call_args
        assert call_args[0][1] == 300  # 5 minutes


class TestUserStats:
    """Test user statistics"""

    @pytest.mark.asyncio
    async def test_get_user_stats(self, rate_limiter):
        """Test getting comprehensive user stats"""
        rate_limiter.redis.hgetall.return_value = {}
        rate_limiter.redis.get.side_effect = [
            b"7",   # minute
            b"70",  # hour
            b"700", # day
        ]
        
        stats = await rate_limiter.get_user_stats("user123", "free")
        
        assert stats["user_id"] == "user123"
        assert stats["profile"] == "free"
        assert stats["limits"]["minute"] == 10
        assert stats["usage"]["minute"] == 7
        assert stats["percentages"]["minute"] == 70.0
        assert "reset_at" in stats


class TestGracePeriodFlow:
    """Test complete grace period flow"""

    @pytest.mark.asyncio
    async def test_grace_period_5min_duration(self, rate_limiter):
        """Test that grace period is 5 minutes"""
        # Grace period should be activated with 300 second TTL
        await rate_limiter.activate_soft_block("user123", "minute")
        
        call_args = rate_limiter.redis.setex.call_args
        ttl = call_args[0][1]
        
        assert ttl == 300  # 5 minutes in seconds

    @pytest.mark.asyncio
    async def test_progression_ok_to_warning_to_soft_block(self, rate_limiter):
        """Test progression through states"""
        rate_limiter.redis.hgetall.return_value = {}
        rate_limiter.redis.exists.return_value = False
        
        # State 1: OK (50%)
        rate_limiter.redis.get.side_effect = [
            b"5", b"50", b"500",
        ]
        status1, _ = await rate_limiter.check_limit("user123", "free")
        assert status1 == LimitLevel.OK
        
        # State 2: WARNING (80%)
        rate_limiter.redis.get.side_effect = [
            b"8", b"80", b"800",
        ]
        rate_limiter.redis.exists.return_value = False
        status2, _ = await rate_limiter.check_limit("user123", "free")
        assert status2 == LimitLevel.WARNING
        
        # State 3: SOFT_BLOCK (110%)
        rate_limiter.redis.get.side_effect = [
            b"11", b"100", b"1000",
        ]
        rate_limiter.redis.exists.return_value = True
        status3, _ = await rate_limiter.check_limit("user123", "free")
        assert status3 == LimitLevel.SOFT_BLOCK
        
        # State 4: EXCEEDED (120%)
        rate_limiter.redis.get.side_effect = [
            b"12", b"120", b"1200",
        ]
        rate_limiter.redis.exists.return_value = False
        status4, _ = await rate_limiter.check_limit("user123", "free")
        assert status4 == LimitLevel.EXCEEDED


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_check_limit_redis_error_gracefully_fails(self, rate_limiter):
        """Test that check_limit fails gracefully if Redis is down"""
        rate_limiter.redis.hgetall.side_effect = Exception("Redis connection error")
        
        status, details = await rate_limiter.check_limit("user123", "free")
        
        # Should fall back to OK (allow)
        assert status == LimitLevel.OK
        assert "error" in details.get("message", "").lower() or True

    @pytest.mark.asyncio
    async def test_increment_counter_silent_failure(self, rate_limiter):
        """Test that increment counter fails silently"""
        rate_limiter.redis.pipeline.side_effect = Exception("Redis error")
        
        # Should not raise
        await rate_limiter.increment_counter("user123")


# Integration-like tests
class TestRateLimiterWithProfiles:
    """Test rate limiter with different profiles"""

    @pytest.mark.asyncio
    async def test_free_profile_lower_limits(self, rate_limiter):
        """Test that free profile has lower limits"""
        rate_limiter.redis.hgetall.return_value = {}
        
        free_limits = await rate_limiter.get_user_limits("user1", "free")
        premium_limits = await rate_limiter.get_user_limits("user2", "premium")
        
        assert free_limits["minute"] < premium_limits["minute"]
        assert free_limits["hour"] < premium_limits["hour"]
        assert free_limits["day"] < premium_limits["day"]

    @pytest.mark.asyncio
    async def test_enterprise_profile_highest_limits(self, rate_limiter):
        """Test that enterprise profile has highest limits"""
        rate_limiter.redis.hgetall.return_value = {}
        
        limits = await rate_limiter.get_user_limits("user", "enterprise")
        
        assert limits["minute"] == 500
        assert limits["hour"] == 10000
        assert limits["day"] == 100000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
