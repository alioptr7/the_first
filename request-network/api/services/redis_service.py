import json
from typing import Any, Optional
from datetime import timedelta

from redis import Redis
from shared.config import settings

# ایجاد اتصال به Redis
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

# پیشوند کلید برای پاسخ‌های کش شده
RESPONSE_CACHE_PREFIX = "response:"
# مدت زمان نگهداری پاسخ‌ها در کش (1 ساعت)
RESPONSE_CACHE_TTL = timedelta(hours=1)


def get_response_cache_key(request_id: str) -> str:
    """ساخت کلید کش برای یک درخواست"""
    return f"{RESPONSE_CACHE_PREFIX}{request_id}"


def get_cached_response(request_id: str) -> Optional[dict[str, Any]]:
    """
    دریافت پاسخ از کش Redis.
    اگر پاسخ در کش نباشد، None برمی‌گرداند.
    """
    cache_key = get_response_cache_key(request_id)
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            return None
    
    return None


def cache_response(request_id: str, response_data: dict[str, Any]) -> None:
    """
    ذخیره پاسخ در کش Redis با TTL مشخص شده.
    """
    cache_key = get_response_cache_key(request_id)
    redis_client.setex(
        cache_key,
        RESPONSE_CACHE_TTL,
        json.dumps(response_data)
    )