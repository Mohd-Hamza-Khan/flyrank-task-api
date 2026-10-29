"""Task CRUD route handlers.

All 7 endpoints (GET /, GET /health, GET /tasks, GET /tasks/{id},
POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}) are grouped in a single
APIRouter. Each handler is a thin delegate that calls a TaskService method
and returns the result.
"""

from fastapi import APIRouter, Depends, status

from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService, get_task_service

router = APIRouter(tags=["Tasks"])


@router.get("/", summary="Welcome message", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint — a simple welcome payload."""
    return {
        "message": "Welcome to the FlyRank Task CRUD API",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health", summary="Service health check", status_code=status.HTTP_200_OK)
async def health_check():
    """Health-check endpoint. Returns `ok` when the service is running."""
    return {"status": "ok"}


@router.get(
    "/tasks",
    summary="List all tasks",
    status_code=status.HTTP_200_OK,
    response_model=list[Task],
)
async def list_tasks(service: TaskService = Depends(get_task_service)):
    """Retrieve every task currently stored in memory."""
    return service.list_tasks()


@router.get(
    "/tasks/{task_id}",
    summary="Get a single task",
    status_code=status.HTTP_200_OK,
    response_model=Task,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Retrieve a single task by its ID."""
    return service.get_task(task_id)


@router.post(
    "/tasks",
    summary="Create a new task",
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    responses={400: {"description": "Invalid request body"}},
)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """Create a new task. The server assigns the ID and timestamp."""
    return service.create_task(task)


@router.put(
    "/tasks/{task_id}",
    summary="Update an existing task",
    status_code=status.HTTP_200_OK,
    response_model=Task,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Replace title/description/status of an existing task by its ID."""
    return service.update_task(task_id, task_update)


@router.delete(
    "/tasks/{task_id}",
    summary="Delete a task",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Task with this ID was not found"}},
)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Delete a task by its ID. Returns 204 with an empty body on success."""
    service.delete_task(task_id)
    return None
