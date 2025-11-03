import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.request import Request
from api.models.response import Response
from api.models.user import User
from api.services.redis_service import RESPONSE_CACHE_PREFIX


@pytest.fixture
def sample_request(db_session: AsyncSession, test_user: User):
    """ایجاد یک درخواست نمونه در دیتابیس"""
    request = Request(
        id=uuid.uuid4(),
        user_id=test_user.id,
        query_type="test_query",
        query_params={"param": "value"},
        status="completed",
        priority=5
    )
    db_session.add(request)
    db_session.commit()
    return request


@pytest.fixture
def sample_response(db_session, sample_request):
    """ایجاد یک پاسخ نمونه در دیتابیس"""
    response = Response(
        id=uuid.uuid4(),
        request_id=sample_request.id,
        result_data={"test": "data"},
        result_count=1,
        execution_time_ms=100,
        received_at=datetime.now(timezone.utc),
        is_cached=False
    )
    db_session.add(response)
    db_session.commit()
    return response


async def test_get_response_not_found(async_client, test_user):
    """تست دریافت پاسخ برای درخواست ناموجود"""
    # ایجاد یک UUID تصادفی
    random_uuid = str(uuid.uuid4())
    
    response = await async_client.get(
        f"/requests/{random_uuid}/response",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


async def test_get_response_unauthorized(async_client, sample_request):
    """تست دریافت پاسخ بدون توکن معتبر"""
    response = await async_client.get(f"/requests/{sample_request.id}/response")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_response_no_response_yet(async_client, sample_request, test_user):
    """تست دریافت پاسخ برای درخواستی که هنوز پاسخ ندارد"""
    response = await async_client.get(
        f"/requests/{sample_request.id}/response",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not available yet" in response.json()["detail"].lower()


async def test_get_response_from_db(async_client, sample_request, sample_response, test_user):
    """تست دریافت پاسخ از دیتابیس"""
    response = await async_client.get(
        f"/requests/{sample_request.id}/response",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["request_id"] == str(sample_request.id)
    assert data["result_data"] == {"test": "data"}
    assert data["result_count"] == 1
    assert data["execution_time_ms"] == 100
    assert not data["is_cached"]


@pytest.mark.usefixtures("redis_client")
async def test_get_response_from_cache(async_client, sample_request, sample_response, test_user, redis_client):
    """تست دریافت پاسخ از کش Redis"""
    # ذخیره پاسخ در کش
    cache_key = f"{RESPONSE_CACHE_PREFIX}{sample_request.id}"
    cached_data = {
        "id": str(sample_response.id),
        "request_id": str(sample_request.id),
        "result_data": {"test": "cached_data"},
        "result_count": 1,
        "execution_time_ms": 100,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "is_cached": True
    }
    redis_client.setex(cache_key, 3600, json.dumps(cached_data))
    
    response = await async_client.get(
        f"/requests/{sample_request.id}/response",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["request_id"] == str(sample_request.id)
    assert data["result_data"] == {"test": "cached_data"}
    assert data["is_cached"]


async def test_get_response_wrong_user(async_client, sample_request, sample_response, other_user):
    """تست دریافت پاسخ توسط کاربر غیرمجاز"""
    response = await async_client.get(
        f"/requests/{sample_request.id}/response",
        headers={"Authorization": f"Bearer {other_user.token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND