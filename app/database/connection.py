"""SQLite connection management."""

import sqlite3

# Default database path: a file named "tasks.db" in the project root.
DB_PATH = "tasks.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a configured sqlite3 Connection.

    - `check_same_thread=False` allows the connection to be shared across
      threads — required because FastAPI's TestClient runs the ASGI app in
      a separate thread.
    - `row_factory = sqlite3.Row` for dict-like column access
    - `PRAGMA foreign_keys = ON` for referential-integrity enforcement.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
