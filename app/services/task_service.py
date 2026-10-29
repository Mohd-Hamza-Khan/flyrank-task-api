"""In-memory task storage and business logic.

The TaskService encapsulates the entire persistence layer: an auto-incrementing
ID counter, a list-based store, and the five CRUD methods. Route handlers
never touch storage directly — they delegate to a TaskService instance,
which can be swapped or reset for testing.
"""

from datetime import datetime
from typing import Optional

from fastapi import Depends

from app.errors.exceptions import TaskNotFoundError
from app.models.task import Task, TaskCreate, TaskUpdate


class TaskService:
    """Encapsulates in-memory task storage and business logic."""

    def __init__(self):
        self._store: list[Task] = []
        self._next_id: int = 1

    def list_tasks(self) -> list[Task]:
        """Return a shallow copy of all stored tasks."""
        return list(self._store)

    def get_task(self, task_id: int) -> Task:
        """Return the task with the given ID, or raise TaskNotFoundError."""
        for task in self._store:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def create_task(self, task_create: TaskCreate) -> Task:
        """Create and store a new task with an auto-generated ID and timestamp."""
        task = Task(
            id=self._next_id,
            title=task_create.title,
            description=task_create.description,
            status=task_create.status,
            created_at=datetime.now(),
        )
        self._store.append(task)
        self._next_id += 1
        return task

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """Replace title/description/status of an existing task by its ID.

        The original created_at timestamp is preserved.
        """
        for index, stored in enumerate(self._store):
            if stored.id == task_id:
                updated = Task(
                    id=stored.id,
                    title=task_update.title,
                    description=task_update.description,
                    status=task_update.status,
                    created_at=stored.created_at,
                )
                self._store[index] = updated
                return updated
        raise TaskNotFoundError(task_id)

    def delete_task(self, task_id: int) -> None:
        """Remove a task by its ID. Raises TaskNotFoundError if it doesn't exist."""
        for index, stored in enumerate(self._store):
            if stored.id == task_id:
                self._store.pop(index)
                return
        raise TaskNotFoundError(task_id)


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

# A single module-level instance is used as the default dependency.
# Tests override this via FastAPI's dependency_overrides to inject a fresh
# TaskService per test.
task_service = TaskService()


def get_task_service() -> TaskService:
    """FastAPI dependency that yields the shared TaskService instance."""
    return task_service
