"""کلاس‌های استثنا برای شبکه درخواست"""
from typing import Any, Dict, Optional

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse

log = structlog.get_logger(__name__)


class RequestNetworkException(Exception):
    """کلاس پایه برای استثناهای شبکه درخواست"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(RequestNetworkException):
    """خطای احراز هویت"""

    def __init__(
        self,
        message: str = "احراز هویت ناموفق بود",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(RequestNetworkException):
    """خطای مجوز"""

    def __init__(
        self,
        message: str = "شما مجوز لازم برای این عملیات را ندارید",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ResourceNotFoundError(RequestNetworkException):
    """خطای منبع یافت نشده"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} با شناسه {resource_id} یافت نشد"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationError(RequestNetworkException):
    """خطای اعتبارسنجی"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )


class DatabaseError(RequestNetworkException):
    """خطای پایگاه داده"""

    def __init__(
        self,
        message: str = "خطای پایگاه داده رخ داده است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(RequestNetworkException):
    """خطای سرویس خارجی"""

    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_message = f"خطا در سرویس {service_name}: {message}"
        super().__init__(
            message=error_message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class ConfigurationError(RequestNetworkException):
    """خطای پیکربندی"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class RateLimitError(RequestNetworkException):
    """خطای محدودیت نرخ"""

    def __init__(
        self,
        message: str = "تعداد درخواست‌های شما از حد مجاز بیشتر شده است",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class InvalidOperationError(RequestNetworkException):
    """خطای عملیات نامعتبر"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DuplicateResourceError(RequestNetworkException):
    """خطای منبع تکراری"""

    def __init__(
        self,
        resource_type: str,
        identifier: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} با مشخصه {identifier} قبلاً ثبت شده است"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class ServiceUnavailableError(RequestNetworkException):
    """خطای عدم دسترسی به سرویس"""

    def __init__(
        self,
        service_name: str,
        message: str = "سرویس در دسترس نیست",
        details: Optional[Dict[str, Any]] = None
    ):
        error_message = f"{service_name}: {message}"
        super().__init__(
            message=error_message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


async def global_exception_handler(request: Request, exc: Exception):
    """
    مدیریت‌کننده خطاهای کلی برای گرفتن خطاهای مدیریت نشده.
    خطا را با جزئیات لاگ می‌کند و یک پاسخ خطای ۵۰۰ استاندارد برمی‌گرداند.
    """
    request_id = getattr(request.state, "request_id", "N/A")
    log.error(
        "خطای مدیریت نشده رخ داده است",
        exc_info=True,
        method=request.method,
        url=str(request.url),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "خطای داخلی سرور رخ داده است",
            "error_id": request_id,
        },
    )