"""Domain exceptions for the task service."""

from fastapi import HTTPException


class TaskNotFoundError(HTTPException):
    """Raised when a task with a given ID does not exist.

    Inherits from HTTPException so it can be raised directly from the service
    layer and mapped to a 404 by a registered exception handler.
    """

    def __init__(self, task_id: int):
        super().__init__(status_code=404, detail=f"Task {task_id} not found")
