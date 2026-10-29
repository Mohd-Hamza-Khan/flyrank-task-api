"""FlyRank Week 2 Assignment A1: Task CRUD API.

A simple, readable FastAPI application providing full CRUD operations
on an in-memory task list. No database, no authentication.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class TaskBase(BaseModel):
    """Fields shared by create and update operations."""

    title: str = Field(..., min_length=1, description="Short title of the task")
    description: Optional[str] = Field(
        None, description="Longer details about the task"
    )
    status: str = Field("todo", description="e.g. todo, in-progress, done")


class TaskCreate(TaskBase):
    """Fields required when creating a new task.

    `TaskBase` already contains exactly what we need, so this subclass is
    mainly a semantic marker — callers POST a TaskCreate and the server
    assigns the ID and timestamp.
    """


class Task(TaskBase):
    """A task as stored in memory (read model)."""

    id: int = Field(..., description="Unique identifier (auto-incremented)")
    created_at: datetime = Field(
        ..., description="Timestamp the task was created"
    )


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

tasks: list[Task] = []
_next_id: int = 1


def _generate_id() -> int:
    """Return the next available task ID and increment the counter."""
    global _next_id
    current = _next_id
    _next_id += 1
    return current


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FlyRank Task CRUD API",
    description=(
        "A simple task-management API built with FastAPI. "
        "All data is stored in memory (no database)."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Convert FastAPI's default 422 response to 400 for invalid request bodies.

    The assignment requires 400 for invalid request bodies; FastAPI/Pydantic
    normally responds with 422 (Unprocessable Entity).
    """
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["Root"], summary="Welcome message")
async def read_root():
    """Root endpoint — a simple welcome payload."""
    return {
        "message": "Welcome to the FlyRank Task CRUD API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"], summary="Service health check")
async def health_check():
    """Health-check endpoint. Returns `ok` when the service is running."""
    return {"status": "ok"}


@app.get("/tasks", tags=["Tasks"], summary="List all tasks", status_code=200)
async def list_tasks():
    """Retrieve every task currently stored in memory."""
    return tasks


@app.get(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Get a single task",
    status_code=200,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def get_task(task_id: int):
    """Retrieve a single task by its ID."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post(
    "/tasks",
    tags=["Tasks"],
    summary="Create a new task",
    status_code=201,
    responses={400: {"description": "Invalid request body"}},
)
async def create_task(task: TaskCreate):
    """Create a new task. The server assigns the ID and timestamp."""
    new_task = Task(
        id=_generate_id(),
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=datetime.now(),
    )
    tasks.append(new_task)
    return new_task


@app.put(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Update an existing task",
    status_code=200,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def update_task(task_id: int, task_update: TaskBase):
    """Replace title/description/status of an existing task by its ID."""
    for index, stored_task in enumerate(tasks):
        if stored_task.id == task_id:
            updated = Task(
                id=stored_task.id,
                title=task_update.title,
                description=task_update.description,
                status=task_update.status,
                created_at=stored_task.created_at,  # keep original timestamp
            )
            tasks[index] = updated
            return updated
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Delete a task",
    status_code=204,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def delete_task(task_id: int):
    """Delete a task by its ID. Returns 204 with an empty body on success."""
    for index, stored_task in enumerate(tasks):
        if stored_task.id == task_id:
            tasks.pop(index)
            return  # FastAPI returns an empty response with 204
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
