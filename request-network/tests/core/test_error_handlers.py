"""تست‌های مربوط به مدیریت خطاها"""
import uuid
from typing import Dict, Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from api.core.error_handlers import setup_error_handlers
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


@pytest.fixture
def test_app():
    """فیکسچر برای ایجاد اپلیکیشن تست"""
    app = FastAPI()
    setup_error_handlers(app)
    return app


@pytest.fixture
def test_client(test_app):
    """فیکسچر برای ایجاد کلاینت تست"""
    return TestClient(test_app)


def create_test_endpoint(app: FastAPI, error: Exception):
    """ایجاد یک اندپوینت تست که خطای مشخص شده را می‌اندازد"""
    @app.get("/test")
    async def test_endpoint():
        raise error
    return test_endpoint


def test_request_network_exception(test_app, test_client):
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


def test_authentication_error(test_app, test_client):
    """تست مدیریت خطای احراز هویت"""
    error = AuthenticationError(
        message="توکن نامعتبر است",
        details={"token": "invalid"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 401
    assert response.json()["detail"] == "توکن نامعتبر است"


def test_authorization_error(test_app, test_client):
    """تست مدیریت خطای مجوز"""
    error = AuthorizationError(
        message="دسترسی غیرمجاز",
        details={"required_role": "admin"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 403
    assert response.json()["detail"] == "دسترسی غیرمجاز"


def test_resource_not_found_error(test_app, test_client):
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


def test_validation_error(test_app, test_client):
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


def test_database_error(test_app, test_client):
    """تست مدیریت خطای پایگاه داده"""
    error = DatabaseError(
        message="خطای اتصال به پایگاه داده",
        details={"connection": "failed"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert response.json()["detail"] == "خطای اتصال به پایگاه داده"


def test_external_service_error(test_app, test_client):
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


def test_configuration_error(test_app, test_client):
    """تست مدیریت خطای پیکربندی"""
    error = ConfigurationError(
        message="تنظیمات ناقص است",
        details={"missing": ["api_key"]}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert response.json()["detail"] == "تنظیمات ناقص است"


def test_rate_limit_error(test_app, test_client):
    """تست مدیریت خطای محدودیت نرخ"""
    error = RateLimitError(
        message="محدودیت نرخ درخواست",
        details={"limit": 100, "period": "1h"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 429
    assert "محدودیت نرخ درخواست" in response.json()["detail"]


def test_invalid_operation_error(test_app, test_client):
    """تست مدیریت خطای عملیات نامعتبر"""
    error = InvalidOperationError(
        message="عملیات نامعتبر است",
        details={"reason": "invalid_state"}
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 400
    assert response.json()["detail"] == "عملیات نامعتبر است"


def test_duplicate_resource_error(test_app, test_client):
    """تست مدیریت خطای منبع تکراری"""
    error = DuplicateResourceError(
        resource_type="کاربر",
        identifier="test@example.com"
    )
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 409
    assert "test@example.com" in response.json()["detail"]


def test_service_unavailable_error(test_app, test_client):
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


def test_unhandled_exception(test_app, test_client):
    """تست مدیریت خطای مدیریت نشده"""
    error = Exception("خطای مدیریت نشده")
    create_test_endpoint(test_app, error)

    response = test_client.get("/test")
    assert response.status_code == 500
    assert "خطای داخلی سرور" in response.json()["detail"]
    assert "error_id" in response.json()