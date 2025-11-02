import json
from typing import Optional

import redis

from core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def get_cached_response(request_id: str) -> Optional[dict]:
    """Get cached response for a request ID."""
    cached_data = redis_client.get(f"response:{request_id}")
    if cached_data:
        return json.loads(cached_data)
    return None

def cache_response(request_id: str, response_data: dict) -> None:
    """Cache response data for a request ID."""
    redis_client.set(
        f"response:{request_id}",
        json.dumps(response_data),
        ex=settings.REDIS_CACHE_TTL
    )