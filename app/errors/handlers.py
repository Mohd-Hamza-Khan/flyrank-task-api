"""Custom exception handlers.

Centralizes the translation of domain/protocol errors into HTTP responses,
keeping route handlers thin and free of HTTP-specific concerns.
"""

from typing import Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.exceptions import TaskNotFoundError


def register_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the given FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ):
        """Convert FastAPI's default 422 response to 400 for invalid request bodies.

        The assignment requires 400 for invalid request bodies; FastAPI/Pydantic
        normally responds with 422 (Unprocessable Entity).
        """
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(_request: Request, exc: TaskNotFoundError):
        """Translate TaskNotFoundError (an HTTPException subclass) to a JSON 404."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
