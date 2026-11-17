"""Request-logging middleware.

Logs method, path, status code, and duration per HTTP request.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

logger = logging.getLogger("uvicorn.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} — status: {response.status_code} — duration: {process_time:.2f}ms"
        )
        return response


def add_logging_middleware(app: ASGIApp) -> ASGIApp:
    """Add request logging middleware to the FastAPI app."""
    app.add_middleware(RequestLoggingMiddleware)
    return app
