"""Database initialization: schema creation and seed data."""

from app.database.connection import get_connection

# The canonical schema. Matches the A1 data model and adds a `done` column
# that is kept synchronized with `status` (todo/in_progress → 0, done → 1).
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'todo',
    done        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
)
"""

# Exactly three example tasks — inserted only when the table is empty.
SEED_TASKS = [
    ("Learn FastAPI", None, "todo", 0, "2026-10-31T00:00:00"),
    ("Implement SQLite database", None, "in_progress", 0, "2026-10-31T00:00:00"),
    ("Write API tests", None, "done", 1, "2026-10-31T00:00:00"),
]


def init_db(db_path: str = "tasks.db") -> None:
    """Create the tasks table and seed initial data if the table is empty.

    This function is idempotent:
    - `CREATE TABLE IF NOT EXISTS` never fails on re-run.
    - Seeding checks `SELECT COUNT(*)` first and only inserts when the table
      is empty, so restarting the app does not create duplicate rows.
    """
    conn = get_connection(db_path)
    conn.execute(CREATE_TABLE_SQL)

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, description, status, done, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            SEED_TASKS,
        )
        conn.commit()

    conn.close()
