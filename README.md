# FlyRank Week 2 Assignment A1 — Task CRUD API

A simple, professional Task CRUD API built with **Python 3.12+** and **FastAPI**.
All data is stored in-memory (no database, no authentication).

The project follows a layered FastAPI layout: the app factory, routes, services,
models, and error handlers each live in their own package.

## Prerequisites

- **Python 3.10+** (tested on 3.12.5)
- **pip** (tested on pip 26.0.1)

## Installation

```bash
# Clone (if not already done)
git clone <repo-url>
cd flyrank-task-api

# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload
```

Once running, the API is available at:

- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Project Structure

```
flyrank-task-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # App factory (create_app) — wiring only
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py        # All 7 route handlers in an APIRouter
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Placeholder for future settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py             # Pydantic schemas (TaskBase, TaskCreate, TaskUpdate, Task)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py     # TaskService — in-memory store + business logic
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── exceptions.py       # Domain exceptions (TaskNotFoundError)
│   │   └── handlers.py         # Exception handlers (422→400, 404 mapping)
│   └── middleware/
│       ├── __init__.py
│       └── logging.py          # Placeholder for request logging
├── tests/
│   ├── __init__.py
│   └── test_tasks.py           # 16 tests covering all endpoints
├── requirements.txt
└── README.md
```

## Architecture overview

- **Routes** (`app/api/routes/tasks.py`) — 7 thin HTTP handlers in an `APIRouter`.
  Each delegates to the `TaskService` and returns the result. No storage logic
  here.
- **Service** (`app/services/task_service.py`) — encapsulates the in-memory
  list store, the ID counter, and all CRUD business logic. Raises
  `TaskNotFoundError` for missing IDs.
- **Models** (`app/models/task.py`) — Pydantic schemas. `TaskCreate` is the
  POST body, `TaskUpdate` is the PUT body (currently identical, kept separate
  for future partial-update support), and `Task` is the read model.
- **Errors** (`app/errors/`) — `exceptions.py` defines domain exceptions;
  `handlers.py` registers handlers that convert them to HTTP responses.
  The `RequestValidationError` handler converts FastAPI's default 422 to 400.
- **App** (`app/main.py`) — the `create_app()` factory wires everything together.
  A module-level `app = create_app()` keeps `uvicorn app.main:app` working.

## Running Tests

```bash
pytest tests/ -v
```

16 tests cover all endpoints, status codes, and edge cases (empty body, 404s, 400s,
and a full create-read-update-delete lifecycle).

To run a single test:

```bash
pytest tests/test_tasks.py::test_create_task_minimal -v
```

---

## API Reference

### `GET /`
Root endpoint — returns a welcome message and links.

**Response** — `200 OK`
```json
{
  "message": "Welcome to the FlyRank Task CRUD API",
  "docs": "/docs",
  "health": "/health"
}
```

---

### `GET /health`
Health-check endpoint.

**Response** — `200 OK`
```json
{ "status": "ok" }
```

---

### `GET /tasks`
List all tasks (empty list if none exist).

**Response** — `200 OK`
```json
[
  {
    "id": 1,
    "title": "Write tests",
    "description": null,
    "status": "todo",
    "created_at": "2026-10-29T06:30:00"
  }
]
```

---

### `GET /tasks/{task_id}`
Retrieve a single task by its ID.

**Response (found)** — `200 OK`
```json
{
  "id": 1,
  "title": "Write tests",
  "description": null,
  "status": "todo",
  "created_at": "2026-10-29T06:30:00"
}
```

**Response (not found)** — `404 Not Found`
```json
{
  "detail": "Task 999 not found"
}
```

---

### `POST /tasks`
Create a new task. The server assigns `id` and `created_at`.

**Request body**
```json
{
  "title": "Write tests",
  "description": "Write comprehensive tests",
  "status": "todo"
}
```

**Response** — `201 Created`
```json
{
  "id": 1,
  "title": "Write tests",
  "description": "Write comprehensive tests",
  "status": "todo",
  "created_at": "2026-10-29T06:30:00"
}
```

**Invalid body** — `400 Bad Request`
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

### `PUT /tasks/{task_id}`
Update an existing task by its ID.

**Request body**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "done"
}
```

**Response (success)** — `200 OK`
```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "status": "done",
  "created_at": "2026-10-29T06:30:00"
}
```

**Response (not found)** — `404 Not Found`
```json
{ "detail": "Task 999 not found" }
```

---

### `DELETE /tasks/{task_id}`
Delete a task by its ID.

**Response (success)** — `204 No Content` (empty body)

**Response (not found)** — `404 Not Found`
```json
{ "detail": "Task 999 not found" }
```
