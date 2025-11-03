"""تست‌های مربوط به مدیریت خطاها"""
import uuid
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient as FastAPITestClient
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from api.core.error_handlers import setup_error_handlers, log_error
from api.core.exceptions import (
    RequestNetworkException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    ConfigurationError,
    RateLimitError,
    InvalidOperationError,
    DuplicateResourceError,
    ServiceUnavailableError
)


class TestModel(BaseModel):
    """مدل تست برای اعتبارسنجی Pydantic"""
    name: str = Field(..., min_length=3)
    age: int = Field(..., ge=0, le=150)


def create_test_endpoint(app: FastAPI, error: Exception):
    """ایجاد یک اندپوینت تست که خطای مشخص شده را می‌اندازد"""
    @app.get("/test")
    async def test_endpoint():
        raise error
    return test_endpoint


def test_request_network_exception(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای پایه شبکه درخواست"""
    error = RequestNetworkException(
        message="خطای تست",
        status_code=400,
        details={"test": "value"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 400
    assert response.json()["detail"] == "خطای تست"


def test_authentication_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای احراز هویت"""
    error = AuthenticationError(
        message="توکن نامعتبر است",
        details={"token": "invalid"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 401
    assert response.json()["detail"] == "توکن نامعتبر است"


def test_authorization_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای مجوز"""
    error = AuthorizationError(
        message="دسترسی غیرمجاز",
        details={"required_role": "admin"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 403
    assert response.json()["detail"] == "دسترسی غیرمجاز"


def test_resource_not_found_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای منبع یافت نشده"""
    resource_id = uuid.uuid4()
    error = ResourceNotFoundError(
        resource_type="کاربر",
        resource_id=resource_id
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 404
    assert f"کاربر با شناسه {resource_id}" in response.json()["detail"]


def test_validation_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای اعتبارسنجی"""
    error = ValidationError(
        message="داده نامعتبر است",
        field="email",
        details={"format": "email"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 422
    assert response.json()["detail"] == "داده نامعتبر است"


def test_database_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای پایگاه داده"""
    error = DatabaseError(
        message="خطای اتصال به پایگاه داده",
        details={"connection": "failed"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert response.json()["detail"] == "خطای اتصال به پایگاه داده"


def test_external_service_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای سرویس خارجی"""
    error = ExternalServiceError(
        service_name="Elasticsearch",
        message="خطای اتصال",
        details={"status": "timeout"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 502
    assert "Elasticsearch" in response.json()["detail"]
    assert "خطای اتصال" in response.json()["detail"]


def test_configuration_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای پیکربندی"""
    error = ConfigurationError(
        message="تنظیمات ناقص است",
        details={"missing": ["api_key"]}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert response.json()["detail"] == "تنظیمات ناقص است"


def test_rate_limit_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای محدودیت نرخ"""
    error = RateLimitError(
        message="محدودیت نرخ درخواست",
        details={"limit": 100, "period": "1h"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 429
    assert "محدودیت نرخ درخواست" in response.json()["detail"]


def test_invalid_operation_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای عملیات نامعتبر"""
    error = InvalidOperationError(
        message="عملیات نامعتبر است",
        details={"reason": "invalid_state"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 400
    assert response.json()["detail"] == "عملیات نامعتبر است"


def test_duplicate_resource_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای منبع تکراری"""
    error = DuplicateResourceError(
        resource_type="کاربر",
        identifier="test@example.com"
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 409
    assert "test@example.com" in response.json()["detail"]


def test_service_unavailable_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای عدم دسترسی به سرویس"""
    error = ServiceUnavailableError(
        service_name="Elasticsearch",
        message="سرویس در حال تعمیر است"
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 503
    assert "Elasticsearch" in response.json()["detail"]
    assert "سرویس در حال تعمیر است" in response.json()["detail"]


def test_unhandled_exception(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای مدیریت نشده"""
    error = Exception("خطای مدیریت نشده")
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert "خطای داخلی سرور" in response.json()["detail"]
    assert "error_id" in response.json()


def test_pydantic_validation_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای اعتبارسنجی Pydantic"""
    @test_app.post("/test_validation")
    async def test_validation(data: TestModel):
        return data

    # تست برای نام کوتاه
    response = test_client.post("/test_validation", json={"name": "ab", "age": 25})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["type"] == "string_too_short" for error in errors)

    # تست برای سن نامعتبر
    response = test_client.post("/test_validation", json={"name": "test", "age": 200})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["type"] == "less_than_equal" for error in errors)


def test_sqlalchemy_error(
    test_app: FastAPI,
    test_client: FastAPITestClient
):
    """تست مدیریت خطای SQLAlchemy"""
    error = SQLAlchemyError("خطای پایگاه داده")
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert "خطای داخلی سرور" in response.json()["detail"]
    assert "error_id" in response.json()


@pytest.mark.asyncio
async def test_log_error():
    """تست تابع لاگ کردن خطا"""
    # ایجاد یک درخواست مصنوعی
    request = AsyncMock()
    request.method = "GET"
    request.url.path = "/test"
    request.headers = {"X-Test": "test"}
    request.query_params = {"q": "test"}
    request.state.request_id = str(uuid.uuid4())
    request.state.user_id = uuid.uuid4()

    # ایجاد یک سرویس لاگینگ مصنوعی
    logging_service_mock = AsyncMock()
    request.app.state.db = AsyncMock()

    with patch("api.services.logging.LoggingService", return_value=logging_service_mock):
        await log_error(
            request=request,
            error_type="TestError",
            error_message="پیام خطای تست",
            status_code=500,
            user_id=request.state.user_id,
            stack_trace="stack trace",
            metadata={"extra": "data"}
        )

    # بررسی فراخوانی متد create_error_log با پارامترهای درست
    logging_service_mock.create_error_log.assert_called_once()
    call_args = logging_service_mock.create_error_log.call_args[1]
    
    assert call_args["error_log"]["error_type"] == "TestError"
    assert call_args["error_log"]["error_message"] == "پیام خطای تست"
    assert call_args["error_log"]["stack_trace"] == "stack trace"
    assert call_args["error_log"]["source"] == "GET /test"
    assert call_args["error_log"]["severity"] == "high"  # چون status_code = 500
    assert call_args["error_log"]["status"] == "new"
    assert call_args["error_log"]["request_id"] == request.state.request_id
    assert call_args["error_log"]["user_id"] == request.state.user_id
    assert call_args["error_log"]["metadata"]["extra"] == "data"


@pytest.mark.asyncio
async def test_log_error_with_logging_error():
    """تست رفتار log_error در صورت بروز خطا در لاگینگ"""
    request = AsyncMock()
    request.method = "GET"
    request.url.path = "/test"
    request.headers = {"X-Test": "test"}
    request.query_params = {"q": "test"}
    request.state.request_id = str(uuid.uuid4())
    request.state.user_id = uuid.uuid4()
    
    # شبیه‌سازی خطا در لاگینگ
    logging_service_mock = AsyncMock()
    logging_service_mock.create_error_log.side_effect = Exception("خطای لاگینگ")
    request.app.state.db = AsyncMock()

    with patch("api.services.logging.LoggingService", return_value=logging_service_mock):
        # خطا نباید به بیرون درز کند
        await log_error(
            request=request,
            error_type="TestError",
            error_message="پیام خطای تست",
            status_code=500,
            user_id=request.state.user_id,
            stack_trace="stack trace",
            metadata={"extra": "data"}
        )