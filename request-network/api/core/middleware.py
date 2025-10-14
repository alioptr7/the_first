import time
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

log = structlog.get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique request_id into the context of each request for traceability.
    It also logs the request details and processing time.
    """



    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind the request_id to the logger context for this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        log.info("Request started", method=request.method, url=str(request.url))

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        log.info("Request finished", status_code=response.status_code, process_time_ms=f"{process_time:.2f}")

        response.headers["X-Request-ID"] = request_id
        return response
