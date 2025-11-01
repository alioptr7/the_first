"""تست‌های مربوط به کلاس‌های استثنا"""
import uuid

import pytest
from fastapi import status

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


def test_request_network_exception():
    """تست کلاس پایه استثنا"""
    message = "خطای تست"
    status_code = 400
    details = {"test": "value"}

    exc = RequestNetworkException(
        message=message,
        status_code=status_code,
        details=details
    )

    assert str(exc) == message
    assert exc.status_code == status_code
    assert exc.details == details


def test_authentication_error():
    """تست کلاس خطای احراز هویت"""
    message = "توکن نامعتبر است"
    details = {"token": "invalid"}

    exc = AuthenticationError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.details == details

    # تست پیام پیش‌فرض
    exc = AuthenticationError()
    assert str(exc) == "احراز هویت ناموفق بود"


def test_authorization_error():
    """تست کلاس خطای مجوز"""
    message = "دسترسی غیرمجاز"
    details = {"required_role": "admin"}

    exc = AuthorizationError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.details == details

    # تست پیام پیش‌فرض
    exc = AuthorizationError()
    assert str(exc) == "شما مجوز لازم برای این عملیات را ندارید"


def test_resource_not_found_error():
    """تست کلاس خطای منبع یافت نشده"""
    resource_type = "کاربر"
    resource_id = uuid.uuid4()
    details = {"additional": "info"}

    exc = ResourceNotFoundError(
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )

    assert f"{resource_type} با شناسه {resource_id}" in str(exc)
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.details == details


def test_validation_error():
    """تست کلاس خطای اعتبارسنجی"""
    message = "داده نامعتبر است"
    field = "email"
    details = {"format": "email"}

    exc = ValidationError(message=message, field=field, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.details["field"] == field
    assert exc.details["format"] == "email"


def test_database_error():
    """تست کلاس خطای پایگاه داده"""
    message = "خطای اتصال به پایگاه داده"
    details = {"connection": "failed"}

    exc = DatabaseError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.details == details

    # تست پیام پیش‌فرض
    exc = DatabaseError()
    assert str(exc) == "خطای پایگاه داده رخ داده است"


def test_external_service_error():
    """تست کلاس خطای سرویس خارجی"""
    service_name = "Elasticsearch"
    message = "خطای اتصال"
    details = {"status": "timeout"}

    exc = ExternalServiceError(
        service_name=service_name,
        message=message,
        details=details
    )

    assert service_name in str(exc)
    assert message in str(exc)
    assert exc.status_code == status.HTTP_502_BAD_GATEWAY
    assert exc.details == details


def test_configuration_error():
    """تست کلاس خطای پیکربندی"""
    message = "تنظیمات ناقص است"
    details = {"missing": ["api_key"]}

    exc = ConfigurationError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.details == details


def test_rate_limit_error():
    """تست کلاس خطای محدودیت نرخ"""
    message = "محدودیت نرخ درخواست"
    details = {"limit": 100, "period": "1h"}

    exc = RateLimitError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exc.details == details

    # تست پیام پیش‌فرض
    exc = RateLimitError()
    assert str(exc) == "تعداد درخواست‌های شما از حد مجاز بیشتر شده است"


def test_invalid_operation_error():
    """تست کلاس خطای عملیات نامعتبر"""
    message = "عملیات نامعتبر است"
    details = {"reason": "invalid_state"}

    exc = InvalidOperationError(message=message, details=details)

    assert str(exc) == message
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.details == details


def test_duplicate_resource_error():
    """تست کلاس خطای منبع تکراری"""
    resource_type = "کاربر"
    identifier = "test@example.com"
    details = {"field": "email"}

    exc = DuplicateResourceError(
        resource_type=resource_type,
        identifier=identifier,
        details=details
    )

    assert resource_type in str(exc)
    assert identifier in str(exc)
    assert exc.status_code == status.HTTP_409_CONFLICT
    assert exc.details == details


def test_service_unavailable_error():
    """تست کلاس خطای عدم دسترسی به سرویس"""
    service_name = "Elasticsearch"
    message = "سرویس در حال تعمیر است"
    details = {"maintenance_window": "1h"}

    exc = ServiceUnavailableError(
        service_name=service_name,
        message=message,
        details=details
    )

    assert service_name in str(exc)
    assert message in str(exc)
    assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exc.details == details

    # تست پیام پیش‌فرض
    exc = ServiceUnavailableError(service_name=service_name)
    assert "سرویس در دسترس نیست" in str(exc)