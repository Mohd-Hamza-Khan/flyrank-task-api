"""Centralized SQLite database management.

Provides a `DB_PATH` default, an `init_db()` helper that creates the schema
using `CREATE TABLE IF NOT EXISTS`, and a `get_connection()` factory that
returns a properly configured connection (row factory, foreign keys, isolation
control).
"""

import sqlite3
from pathlib import Path

# Default database path: a file named "tasks.db" in the project root.
DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "tasks.db")


def init_db(db_path: str = DB_PATH) -> None:
    """Create the tasks table if it does not already exist."""
    conn = get_connection(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL CHECK(length(title) > 0),
            description TEXT,
            status      TEXT    NOT NULL DEFAULT 'todo',
            created_at  REAL    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a configured sqlite3 Connection.

    - `check_same_thread=False` allows the connection to be shared across
      threads — required because FastAPI's TestClient runs the ASGI app in
      a separate thread.
    - `row_factory = sqlite3.Row` for dict-like column access
    - `PRAGMA foreign_keys = ON` for referential-integrity enforcement
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
