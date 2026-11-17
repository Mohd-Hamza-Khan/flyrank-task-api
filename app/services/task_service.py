"""SQLite-backed task storage and business logic.

The TaskService encapsulates the entire persistence layer: a SQLite database
connection via `app.database.connection`, table initialization, and the five
CRUD methods with `done`/`status` synchronization.
"""

import sqlite3
from datetime import datetime

from fastapi import Depends

from app.database.connection import DB_PATH, get_connection
from app.database.initialization import init_db
from app.errors.exceptions import TaskNotFoundError
from app.models.task import Task, TaskCreate, TaskUpdate


class TaskService:
    """Encapsulates SQLite-backed task storage and business logic."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(db_path)
        self._conn: sqlite3.Connection = get_connection(db_path)

    def _parse_created_at(self, val) -> datetime:
        """Parse created_at stored as TEXT (ISO string) or REAL (timestamp)."""
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val)
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except ValueError:
                return datetime.now()
        return datetime.now()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert a sqlite3.Row into a Task Pydantic model."""
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            done=row["done"],
            created_at=self._parse_created_at(row["created_at"]),
        )

    def list_tasks(self) -> list[Task]:
        """Return all stored tasks, ordered by ID."""
        rows = self._conn.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_task(self, task_id: int) -> Task:
        """Return the task with the given ID, or raise TaskNotFoundError."""
        row = self._conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._row_to_task(row)

    def create_task(self, task_create: TaskCreate) -> Task:
        """Create and store a new task with an auto-generated ID and timestamp."""
        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        done = 1 if task_create.status == "done" else 0
        cursor = self._conn.execute(
            "INSERT INTO tasks (title, description, status, done, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                task_create.title,
                task_create.description,
                task_create.status,
                done,
                now_str,
            ),
        )
        self._conn.commit()
        task_id = cursor.lastrowid
        row = self._conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return self._row_to_task(row)

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task:
        """Replace title/description/status of an existing task by its ID.

        The original created_at timestamp is preserved. `done` is synchronized with `status`.
        """
        done = 1 if task_update.status == "done" else 0
        cursor = self._conn.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ?, done = ? WHERE id = ?",
            (
                task_update.title,
                task_update.description,
                task_update.status,
                done,
                task_id,
            ),
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            raise TaskNotFoundError(task_id)
        row = self._conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return self._row_to_task(row)

    def delete_task(self, task_id: int) -> None:
        """Remove a task by its ID. Raises TaskNotFoundError if it doesn't exist."""
        cursor = self._conn.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            raise TaskNotFoundError(task_id)

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()


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
