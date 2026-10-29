"""Tests for the FlyRank Task CRUD API (Stage 2).

Uses FastAPI's TestClient which is built on httpx under the hood.
No external server is needed — the app runs in-process.
"""

import pytest
from fastapi.testclient import TestClient

from main import app, tasks, _next_id


client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_storage():
    """Clear the in-memory task list before each test for isolation."""
    tasks.clear()
    # Reset the ID counter
    import main
    main._next_id = 1
    yield
    tasks.clear()
    main._next_id = 1


# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------


def test_root():
    """GET / returns 200 and a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "health" in data


def test_health():
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------


def test_list_tasks_empty():
    """GET /tasks returns 200 and an empty list when no tasks exist."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_non_empty():
    """GET /tasks returns 200 and all stored tasks."""
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task A"
    assert data[1]["title"] == "Task B"


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------


def test_get_task_existing():
    """GET /tasks/{id} returns 200 for a valid ID."""
    create_res = client.post("/tasks", json={"title": "My Task"})
    task_id = create_res.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "My Task"
    assert task["status"] == "todo"
    assert "created_at" in task


def test_get_task_not_found():
    """GET /tasks/{id} returns 404 for an unknown ID."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------


def test_create_task_minimal():
    """POST /tasks with only required fields returns 201."""
    response = client.post("/tasks", json={"title": "Simple Task"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Simple Task"
    assert task["description"] is None
    assert task["status"] == "todo"
    assert task["id"] == 1
    assert "created_at" in task


def test_create_task_full():
    """POST /tasks with all optional fields returns 201."""
    response = client.post(
        "/tasks",
        json={
            "title": "Full Task",
            "description": "A detailed description",
            "status": "in-progress",
        },
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Full Task"
    assert task["description"] == "A detailed description"
    assert task["status"] == "in-progress"
    assert task["id"] == 1


def test_create_task_invalid_body():
    """POST /tasks with an empty body returns 400."""
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_create_task_empty_title():
    """POST /tasks with an empty title returns 400."""
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# PUT /tasks/{id}
# ---------------------------------------------------------------------------


def test_update_task_existing():
    """PUT /tasks/{id} returns 200 and updated fields."""
    create_res = client.post("/tasks", json={"title": "Original"})
    task_id = create_res.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated", "description": "New desc", "status": "done"},
    )
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "Updated"
    assert task["description"] == "New desc"
    assert task["status"] == "done"


def test_update_task_not_found():
    """PUT /tasks/{id} returns 404 for an unknown ID."""
    response = client.put(
        "/tasks/999",
        json={"title": "Updated"},
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_task_invalid_body():
    """PUT /tasks/{id} with an invalid body returns 400."""
    create_res = client.post("/tasks", json={"title": "Original"})
    task_id = create_res.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------


def test_delete_task_existing():
    """DELETE /tasks/{id} returns 204 with an empty body."""
    create_res = client.post("/tasks", json={"title": "To Delete"})
    task_id = create_res.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.content == b""

    # Confirm the task is gone
    follow_up = client.get(f"/tasks/{task_id}")
    assert follow_up.status_code == 404


def test_delete_task_not_found():
    """DELETE /tasks/{id} returns 404 for an unknown ID."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Full lifecycle
# ---------------------------------------------------------------------------


def test_full_lifecycle():
    """Create, read, update, delete, verify gone — one task end-to-end."""
    # Create
    create_res = client.post("/tasks", json={"title": "Lifecycle Task"})
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]

    # Read
    read_res = client.get(f"/tasks/{task_id}")
    assert read_res.status_code == 200
    assert read_res.json()["title"] == "Lifecycle Task"

    # Update
    update_res = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Lifecycle", "status": "done"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "done"

    # Delete
    delete_res = client.delete(f"/tasks/{task_id}")
    assert delete_res.status_code == 204

    # Verify gone
    gone_res = client.get(f"/tasks/{task_id}")
    assert gone_res.status_code == 404
