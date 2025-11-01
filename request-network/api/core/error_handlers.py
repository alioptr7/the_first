"""سیستم مدیریت خطاها"""
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from api.core.exceptions import (
    RequestNetworkException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError as CustomValidationError,
    DatabaseError,
    ExternalServiceError
)
from api.services.logging import LoggingService


logger = logging.getLogger(__name__)


async def log_error(
    request: Request,
    error_type: str,
    error_message: str,
    status_code: int,
    user_id: Optional[UUID] = None,
    stack_trace: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """ثبت خطا در سیستم لاگینگ"""
    try:
        db = request.app.state.db
        logging_service = LoggingService(db)
        await logging_service.create_error_log(
            error_log={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
                "source": f"{request.method} {request.url.path}",
                "severity": "high" if status_code >= 500 else "medium",
                "status": "new",
                "request_id": getattr(request.state, "request_id", None),
                "user_id": user_id,
                "metadata": {
                    "status_code": status_code,
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                    **(metadata or {})
                }
            },
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"خطا در ثبت لاگ خطا: {str(e)}")


def setup_error_handlers(app: FastAPI) -> None:
    """تنظیم مدیریت‌کننده‌های خطا"""

    @app.exception_handler(RequestNetworkException)
    async def handle_request_network_exception(
        request: Request,
        exc: RequestNetworkException
    ) -> JSONResponse:
        """مدیریت خطاهای سفارشی شبکه درخواست"""
        await log_error(
            request=request,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            status_code=exc.status_code,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)}
        )

    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(
        request: Request,
        exc: AuthenticationError
    ) -> JSONResponse:
        """مدیریت خطاهای احراز هویت"""
        await log_error(
            request=request,
            error_type="AuthenticationError",
            error_message=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)}
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(
        request: Request,
        exc: AuthorizationError
    ) -> JSONResponse:
        """مدیریت خطاهای مجوز"""
        await log_error(
            request=request,
            error_type="AuthorizationError",
            error_message=str(exc),
            status_code=status.HTTP_403_FORBIDDEN,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ResourceNotFoundError)
    async def handle_not_found_error(
        request: Request,
        exc: ResourceNotFoundError
    ) -> JSONResponse:
        """مدیریت خطاهای منبع یافت نشده"""
        await log_error(
            request=request,
            error_type="ResourceNotFoundError",
            error_message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        )

    @app.exception_handler(CustomValidationError)
    async def handle_validation_error(
        request: Request,
        exc: CustomValidationError
    ) -> JSONResponse:
        """مدیریت خطاهای اعتبارسنجی سفارشی"""
        await log_error(
            request=request,
            error_type="ValidationError",
            error_message=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation_error(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """مدیریت خطاهای اعتبارسنجی Pydantic"""
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })

        await log_error(
            request=request,
            error_type="PydanticValidationError",
            error_message="خطای اعتبارسنجی داده",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            user_id=getattr(request.state, "user_id", None),
            metadata={"validation_errors": errors}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors}
        )

    @app.exception_handler(DatabaseError)
    async def handle_database_error(
        request: Request,
        exc: DatabaseError
    ) -> JSONResponse:
        """مدیریت خطاهای پایگاه داده"""
        await log_error(
            request=request,
            error_type="DatabaseError",
            error_message=str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "خطای پایگاه داده رخ داده است"}
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(
        request: Request,
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """مدیریت خطاهای SQLAlchemy"""
        await log_error(
            request=request,
            error_type="SQLAlchemyError",
            error_message=str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_id=getattr(request.state, "user_id", None),
            stack_trace=exc.__traceback__
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "خطای پایگاه داده رخ داده است"}
        )

    @app.exception_handler(ExternalServiceError)
    async def handle_external_service_error(
        request: Request,
        exc: ExternalServiceError
    ) -> JSONResponse:
        """مدیریت خطاهای سرویس‌های خارجی"""
        await log_error(
            request=request,
            error_type="ExternalServiceError",
            error_message=str(exc),
            status_code=status.HTTP_502_BAD_GATEWAY,
            user_id=getattr(request.state, "user_id", None)
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """مدیریت سایر خطاها"""
        await log_error(
            request=request,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_id=getattr(request.state, "user_id", None),
            stack_trace=exc.__traceback__
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "خطای داخلی سرور رخ داده است"}
        )