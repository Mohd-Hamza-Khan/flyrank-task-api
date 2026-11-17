# FlyRank Week 3 Assignment A2 — Task CRUD API (SQLite Integration)

A professional, robust Task CRUD API built with **Python 3.10+** and **FastAPI**.
All task data is persistently stored in a SQLite database (using Python's built-in `sqlite3` library).
No authentication.

The project follows a layered FastAPI architecture: app factory, API routes, database layer, service layer, models, and error handlers each live in their own modular packages.

---

## Key Features (Assignment A2)
- **SQLite Persistence**: Centralized connection management (`app/database/connection.py`) with `row_factory=sqlite3.Row` and foreign key enforcement.
- **Idempotent Initialization & Seeding**: Automatically creates the `tasks` table and seeds **3 example tasks** (`Learn FastAPI`, `Implement SQLite database`, `Write API tests`) if the table is empty (`app/database/initialization.py`).
- **Done/Status Synchronization**: Includes the `done` integer column (`0` for `todo`/`in_progress`, `1` for `done`), automatically synchronized with `status`.
- **Robust Test Suite**: Comprehensive `pytest` test suite covering database initialization, idempotency, seed tasks, and all 7 API CRUD endpoints.

---

## Prerequisites

- **Python 3.10+**
- **pip**

---

## Installation & Running

```bash
# Navigate into the project directory
cd flyrank-task-api

# Install dependencies
pip install -r requirements.txt

# Run the API server with auto-reload
uvicorn app.main:app --reload
```

Once running, the API is available at:
- **API Root**: http://127.0.0.1:8000
- **Interactive Swagger UI Docs**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc

---

## Project Structure

```
flyrank-task-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # App factory (create_app)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py        # All 7 route handlers in an APIRouter
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration (DB_PATH settings)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # SQLite connection manager
│   │   └── initialization.py   # Schema creation & idempotent seeding
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py             # Pydantic schemas (Task, TaskCreate, TaskUpdate)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py     # SQLite storage + done/status sync
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── exceptions.py       # Domain exceptions (TaskNotFoundError)
│   │   └── handlers.py         # Exception handlers (422→400, 404 mapping)
│   └── middleware/
│       ├── __init__.py
│       └── logging.py          # Request logging middleware
├── tests/
│   ├── __init__.py
│   ├── test_tasks.py           # API integration tests
│   └── test_database.py        # Database schema & seeding tests
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
└── tasks.db                    # SQLite database file (gitignored)
```

---

## Running Tests

```bash
pytest tests/ -v
```

To run a specific test file:
```bash
pytest tests/test_tasks.py -v
pytest tests/test_database.py -v
```

---

## API Reference

### `GET /`
Root endpoint — returns a welcome message and links.

### `GET /health`
Health-check endpoint (`{"status": "ok"}`).

### `GET /tasks`
List all tasks (returns 3 pre-seeded tasks by default on a fresh database).

**Response** — `200 OK`
```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": null,
    "status": "todo",
    "done": 0,
    "created_at": "2026-10-31T00:00:00"
  }
]
```

### `GET /tasks/{task_id}`
Retrieve a single task by its ID.

### `POST /tasks`
Create a new task. The server assigns `id`, `created_at`, and synchronizes `done`.

**Request body**
```json
{
  "title": "Write SQLite tests",
  "description": "Test database persistence",
  "status": "in-progress"
}
```

### `PUT /tasks/{task_id}`
Update an existing task by its ID.

### `DELETE /tasks/{task_id}`
Delete a task by its ID (`204 No Content`).
