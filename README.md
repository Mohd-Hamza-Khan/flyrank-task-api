# FlyRank Week 2 Assignment A1 — Task CRUD API

A simple Task CRUD API built with **Python 3.12+** and **FastAPI**.
All data is stored in-memory (no database, no authentication).

Two implementations are provided:

| Version | Description | Entry Point |
|---------|-------------|-------------|
| **Hand-built** | Straightforward, beginner-readable code with inline list storage | `main.py` (root) |

---

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

### Hand-built version

```bash
uvicorn main:app --reload
```


Once running, the API is available at:

- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

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
  "description": "Write comprehensive tests",  // optional
  "status": "todo"                              // optional, defaults to "todo"
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

---

## Running Tests

```bash
pytest test_main.py -v
```

16 tests cover all endpoints, status codes, and edge cases (empty body, 404s, 400s).

---

## Project Structure

```
flyrank-task-api/
├── main.py              # Hand-built implementation
├── test_main.py         # Tests for hand-built version
├── requirements.txt     # Python dependencies
```

