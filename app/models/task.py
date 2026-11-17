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
    """Fields required when creating a new task."""


class TaskUpdate(TaskBase):
    """Fields required when updating an existing task."""


class Task(TaskBase):
    """A task as stored in the database (read model)."""

    id: int = Field(..., description="Unique identifier (auto-incremented)")
    done: int = Field(0, description="1 if done, 0 otherwise")
    created_at: datetime = Field(
        ..., description="Timestamp the task was created"
    )
