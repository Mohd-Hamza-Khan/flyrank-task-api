"""Pydantic data models for the Task CRUD API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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


class TaskUpdate(TaskBase):
    """Fields required when updating an existing task.

    Currently mirrors TaskCreate (full replace, not a partial patch), but
    kept as a separate schema so partial-update support can be added later
    without affecting the create contract.
    """


class Task(TaskBase):
    """A task as stored in memory (read model)."""

    id: int = Field(..., description="Unique identifier (auto-incremented)")
    created_at: datetime = Field(
        ..., description="Timestamp the task was created"
    )
