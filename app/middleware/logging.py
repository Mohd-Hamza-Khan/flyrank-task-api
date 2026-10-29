"""Skeleton: request-logging middleware.

No behavior wired in yet — the module exists so the concern has its own home.
A real implementation would log method, path, status, and duration per request.
"""

from starlette.types import ASGIApp


def add_logging_middleware(app: ASGIApp) -> ASGIApp:
    """Placeholder for future request-logging middleware."""
    return app
