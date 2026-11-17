"""Tests for SQLite database initialization, schema, seeding, and idempotency."""

import os
import sqlite3
import pytest
from app.database.connection import get_connection
from app.database.initialization import init_db, SEED_TASKS


def test_database_initialization_and_seeding(tmp_path):
    """Verify that init_db creates the table and seeds exactly 3 tasks when empty."""
    db_file = tmp_path / "test_tasks.db"
    db_path = str(db_file)

    # Initialize DB on fresh file
    init_db(db_path)
    assert db_file.exists()

    conn = get_connection(db_path)

    # Verify schema columns
    cursor = conn.execute("PRAGMA table_info(tasks)")
    columns = {row["name"] for row in cursor.fetchall()}
    expected_columns = {"id", "title", "description", "status", "done", "created_at"}
    assert expected_columns.issubset(columns)

    # Verify exactly 3 seed tasks
    rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    assert len(rows) == 3

    assert rows[0]["title"] == "Learn FastAPI"
    assert rows[0]["status"] == "todo"
    assert rows[0]["done"] == 0

    assert rows[1]["title"] == "Implement SQLite database"
    assert rows[1]["status"] == "in_progress"
    assert rows[1]["done"] == 0

    assert rows[2]["title"] == "Write API tests"
    assert rows[2]["status"] == "done"
    assert rows[2]["done"] == 1

    conn.close()


def test_database_initialization_idempotency(tmp_path):
    """Verify that calling init_db multiple times does not duplicate seed records."""
    db_file = tmp_path / "idempotent_tasks.db"
    db_path = str(db_file)

    # Initialize multiple times
    init_db(db_path)
    init_db(db_path)
    init_db(db_path)

    conn = get_connection(db_path)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    assert count == 3
    conn.close()
