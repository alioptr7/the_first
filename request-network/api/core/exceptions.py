import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

log = structlog.get_logger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unhandled exceptions.
    Logs the exception with traceback and returns a standardized 500 error response.
    """
    request_id = getattr(request.state, "request_id", "N/A")
    log.error(
        "An unhandled exception occurred",
        exc_info=True,
        method=request.method,
        url=str(request.url),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error_id": request_id,
        },
    )