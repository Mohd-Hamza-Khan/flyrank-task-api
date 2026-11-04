"""Application factory for the FlyRank Task CRUD API.

Creates and configures a single FastAPI app instance: metadata, the tasks
router, custom exception handlers, middleware, and database initialization.
"""

from fastapi import FastAPI

from app.api.routes import tasks
from app.database.initialization import init_db
from app.errors.handlers import register_handlers
from app.middleware.logging import add_logging_middleware


def create_app() -> FastAPI:
    """Build a fully-wired FastAPI application.

    Initializes the SQLite database (creates table + seeds if empty) on every
    startup.
    """
    # Database initialization — idempotent (CREATE IF NOT EXISTS + empty-check seed)
    init_db()

    app = FastAPI(
        title="FlyRank Task CRUD API",
        description=(
            "A simple task-management API built with FastAPI. "
            "All data is stored in a SQLite database."
        ),
        version="2.0.0",
    )

    # Middleware (currently a no-op placeholder)
    add_logging_middleware(app)

    # Exception handlers (422→400, 404 domain mapping)
    register_handlers(app)

    # Routes
    app.include_router(tasks.router)

    return app


# Module-level instance so `uvicorn app.main:app --reload` works.
app = create_app()
