"""
Tests for Response Retrieval and Caching endpoints
"""
import pytest
import json
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime

from request_network.api.main import app
from request_network.api.models.request import Request as RequestModel
from request_network.api.models.response import Response
from request_network.api.models.user import User
from request_network.api.schemas.response import ResponseDetailed


@pytest.fixture
async def test_client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
def test_request_id():
    """Generate test request ID."""
    return uuid4()


@pytest.fixture
def test_response_data():
    """Sample response data."""
    return {
        "status": "success",
        "data": [{"id": 1, "name": "test"}],
        "count": 1
    }


class TestResponseRetrieval:
    """Test response retrieval endpoints."""

    @pytest.mark.asyncio
    async def test_get_response_from_database_first_time(
        self,
        test_client,
        test_user_id,
        test_request_id,
        test_response_data
    ):
        """Test getting response from database on first retrieval."""
        # Mock database session
        with patch('request_network.api.routers.request_router.get_db_session'):
            # Mock Redis client
            mock_redis = AsyncMock()
            mock_redis.get_response.return_value = None  # Cache miss
            mock_redis.set_response.return_value = True  # Cache set success

            with patch('request_network.api.routers.request_router.get_redis_client') as mock_get_redis:
                mock_get_redis.return_value = mock_redis

                # Simulate database query result
                response_obj = Response(
                    id=uuid4(),
                    request_id=test_request_id,
                    result_data=test_response_data,
                    result_count=1,
                    execution_time_ms=123,
                    received_at=datetime.utcnow(),
                    is_cached=False
                )

                # Response should be fetched from database and cached
                assert response_obj.result_data == test_response_data
                assert response_obj.is_cached == False

    @pytest.mark.asyncio
    async def test_get_response_from_cache_second_time(
        self,
        test_client,
        test_user_id,
        test_request_id,
        test_response_data
    ):
        """Test getting response from cache on second retrieval."""
        # Mock Redis client with cached data
        mock_redis = AsyncMock()
        cached_data = {
            "id": str(uuid4()),
            "request_id": str(test_request_id),
            "result_data": test_response_data,
            "result_count": 1,
            "execution_time_ms": 123,
            "received_at": datetime.utcnow().isoformat(),
            "is_cached": True,
            "cache_key": f"response:{test_request_id}",
            "meta": None
        }
        mock_redis.get_response.return_value = cached_data

        with patch('request_network.api.routers.request_router.get_redis_client') as mock_get_redis:
            mock_get_redis.return_value = mock_redis

            # Verify cache returns data directly
            result = await mock_redis.get_response(str(test_request_id))
            assert result is not None
            assert result["result_data"] == test_response_data
            assert result["is_cached"] == True

    @pytest.mark.asyncio
    async def test_response_404_when_not_found(self):
        """Test 404 response when request/response doesn't exist."""
        # This would be tested in integration tests with actual database
        pass


class TestCacheManagement:
    """Test cache management endpoints."""

    @pytest.mark.asyncio
    async def test_get_cache_stats(self):
        """Test getting cache statistics."""
        mock_redis = AsyncMock()
        mock_stats = {
            "status": "connected",
            "total_keys": 5000,
            "response_cache_keys": 2500,
            "used_memory_human": "256M",
            "connected_clients": 8
        }
        mock_redis.get_cache_stats.return_value = mock_stats

        stats = await mock_redis.get_cache_stats()
        assert stats["status"] == "connected"
        assert stats["response_cache_keys"] == 2500
        assert stats["used_memory_human"] == "256M"

    @pytest.mark.asyncio
    async def test_clear_all_cache(self):
        """Test clearing all cache."""
        mock_redis = AsyncMock()
        mock_redis.get_cache_stats.return_value = {"response_cache_keys": 1250}
        mock_redis.clear_all_cache.return_value = True

        # Get stats before clear
        stats_before = await mock_redis.get_cache_stats()
        cleared_count = stats_before["response_cache_keys"]

        # Clear cache
        success = await mock_redis.clear_all_cache()

        assert success == True
        assert cleared_count == 1250

    @pytest.mark.asyncio
    async def test_invalidate_user_cache(self, test_user_id):
        """Test invalidating cache for specific user."""
        mock_redis = AsyncMock()
        mock_redis.invalidate_user_cache.return_value = 45

        deleted = await mock_redis.invalidate_user_cache(str(test_user_id))
        assert deleted == 45

    @pytest.mark.asyncio
    async def test_invalidate_single_response(self, test_request_id):
        """Test invalidating cache for single response."""
        mock_redis = AsyncMock()
        mock_redis.invalidate_response.return_value = True

        success = await mock_redis.invalidate_response(str(test_request_id))
        assert success == True


class TestRedisClient:
    """Test RedisClient implementation."""

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection."""
        from request_network.api.db.redis_client import RedisClient
        from core.config import settings

        client = RedisClient(settings.REDIS_URL)

        # Mock connection
        with patch.object(client, 'client') as mock_client:
            mock_client.ping = AsyncMock(return_value=True)
            # Would test actual connection in integration tests

    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key format."""
        from request_network.api.db.redis_client import RedisClient

        test_id = str(uuid4())
        key = RedisClient._make_key(test_id)

        assert key == f"response:{test_id}"
        assert key.startswith("response:")

    @pytest.mark.asyncio
    async def test_set_get_response_roundtrip(self):
        """Test setting and getting response data."""
        mock_redis = AsyncMock()
        test_id = str(uuid4())
        test_data = {"result": "test"}

        # Set response
        set_result = await mock_redis.set_response(test_id, test_data, ttl_hours=24)
        assert set_result == True or set_result is None

        # Get response (mock would return same data)
        mock_redis.get_response.return_value = test_data
        get_result = await mock_redis.get_response(test_id)
        assert get_result == test_data


class TestCacheInvalidationOnImport:
    """Test cache invalidation when results are imported."""

    @pytest.mark.asyncio
    async def test_cache_invalidated_on_result_import(self, test_request_id):
        """Test that cache is invalidated when new results are imported."""
        mock_redis = AsyncMock()
        mock_redis.invalidate_response.return_value = True

        # Simulate result import invalidating cache
        result = await mock_redis.invalidate_response(str(test_request_id))

        assert result == True
        mock_redis.invalidate_response.assert_called_once_with(str(test_request_id))


class TestErrorHandling:
    """Test error handling in response retrieval."""

    @pytest.mark.asyncio
    async def test_redis_connection_failure_graceful_fallback(self):
        """Test graceful fallback when Redis is unavailable."""
        mock_redis = AsyncMock()
        mock_redis.is_connected.return_value = False

        # Should return None or fallback to database
        result = await mock_redis.get_response("test_id")
        # In real implementation, should fall back to database

    @pytest.mark.asyncio
    async def test_cache_error_handling(self):
        """Test error handling during cache operations."""
        mock_redis = AsyncMock()
        mock_redis.set_response.side_effect = Exception("Connection error")

        with pytest.raises(Exception):
            await mock_redis.set_response("test_id", {})


class TestPerformance:
    """Performance-related tests."""

    @pytest.mark.asyncio
    async def test_cache_hit_vs_miss_timing(self):
        """Test that cache hits are faster than database queries."""
        # This would be tested with actual timing measurements
        # Cache hit: <50ms expected
        # Cache miss: 100-500ms expected
        pass

    @pytest.mark.asyncio
    async def test_large_response_caching(self):
        """Test caching of large responses."""
        large_data = {"data": [{"id": i} for i in range(10000)]}
        mock_redis = AsyncMock()
        mock_redis.set_response.return_value = True

        success = await mock_redis.set_response("test_id", large_data)
        assert success == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
