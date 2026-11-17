"""Tests for the FlyRank Task CRUD API.

Uses FastAPI's TestClient (httpx-backed) so no external server is needed.
Each test gets a fresh in-memory SQLite TaskService via fixture override,
which initializes and seeds the 3 default tasks.
"""

from typing import Generator
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.task import TaskCreate
from app.services.task_service import TaskService, get_task_service


@pytest.fixture
def service() -> TaskService:
    """A fresh TaskService instance backed by an in-memory SQLite database."""
    return TaskService(db_path=":memory:")


@pytest.fixture
def fastapi_app(service: TaskService) -> FastAPI:
    """A FastAPI app with the shared TaskService injected via dependency override."""
    app = create_app()
    app.dependency_overrides[get_task_service] = lambda: service
    return app


@pytest.fixture
def client(fastapi_app: FastAPI) -> Generator[TestClient, None, None]:
    """TestClient for the fresh app."""
    with TestClient(fastapi_app) as c:
        yield c


# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------


def test_root(client: TestClient):
    """GET / returns 200 and a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "health" in data


def test_health(client: TestClient):
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------


def test_list_tasks_seeded(client: TestClient):
    """GET /tasks returns 200 and the 3 default seeded tasks."""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "Learn FastAPI"
    assert data[0]["done"] == 0
    assert data[1]["title"] == "Implement SQLite database"
    assert data[1]["done"] == 0
    assert data[2]["title"] == "Write API tests"
    assert data[2]["done"] == 1


def test_list_tasks_non_empty(client: TestClient, service: TaskService):
    """GET /tasks returns 200 and all stored tasks (3 seeded + 2 new)."""
    service.create_task(TaskCreate(title="Task A", status="todo"))
    service.create_task(TaskCreate(title="Task B", status="done"))

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[3]["title"] == "Task A"
    assert data[3]["done"] == 0
    assert data[4]["title"] == "Task B"
    assert data[4]["done"] == 1


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------


def test_get_task_existing(client: TestClient):
    """GET /tasks/{id} returns 200 for a valid ID (e.g. seed task or created task)."""
    # Seed task 1 exists
    response = client.get("/tasks/1")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["title"] == "Learn FastAPI"
    assert result["status"] == "todo"
    assert result["done"] == 0
    assert "created_at" in result


def test_get_task_not_found(client: TestClient):
    """GET /tasks/{id} returns 404 for an unknown ID."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------


def test_create_task_minimal(client: TestClient):
    """POST /tasks with only required fields returns 201 (ID 4 after 3 seeds)."""
    response = client.post("/tasks", json={"title": "Simple Task"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Simple Task"
    assert task["description"] is None
    assert task["status"] == "todo"
    assert task["done"] == 0
    assert task["id"] == 4
    assert "created_at" in task


def test_create_task_full(client: TestClient):
    """POST /tasks with all optional fields returns 201 (ID 4 after 3 seeds)."""
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
    assert task["done"] == 0
    assert task["id"] == 4


def test_create_task_done_status(client: TestClient):
    """POST /tasks with status 'done' sets done=1."""
    response = client.post(
        "/tasks",
        json={"title": "Finished Task", "status": "done"},
    )
    assert response.status_code == 201
    task = response.json()
    assert task["status"] == "done"
    assert task["done"] == 1


def test_create_task_invalid_body(client: TestClient):
    """POST /tasks with an empty body returns 400."""
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_create_task_empty_title(client: TestClient):
    """POST /tasks with an empty title returns 400."""
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# PUT /tasks/{id}
# ---------------------------------------------------------------------------


def test_update_task_existing(client: TestClient):
    """PUT /tasks/{id} returns 200 and updated fields, updating done flag."""
    # Update seed task 1
    response = client.put(
        "/tasks/1",
        json={"title": "Updated FastAPI", "description": "New desc", "status": "done"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["title"] == "Updated FastAPI"
    assert result["description"] == "New desc"
    assert result["status"] == "done"
    assert result["done"] == 1


def test_update_task_not_found(client: TestClient):
    """PUT /tasks/{id} returns 404 for an unknown ID."""
    response = client.put(
        "/tasks/999",
        json={"title": "Updated"},
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_task_invalid_body(client: TestClient):
    """PUT /tasks/{id} with an invalid body returns 400."""
    response = client.put("/tasks/1", json={})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------


def test_delete_task_existing(client: TestClient):
    """DELETE /tasks/{id} returns 204 with an empty body."""
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""

    # Confirm the task is gone
    follow_up = client.get("/tasks/1")
    assert follow_up.status_code == 404


def test_delete_task_not_found(client: TestClient):
    """DELETE /tasks/{id} returns 404 for an unknown ID."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Full lifecycle
# ---------------------------------------------------------------------------


def test_full_lifecycle(client: TestClient):
    """Create, read, update, delete, verify gone — one task end-to-end."""
    # Create (via API to exercise the full path) -> gets ID 4
    create_res = client.post("/tasks", json={"title": "Lifecycle Task"})
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]
    assert task_id == 4
    assert create_res.json()["done"] == 0

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
    assert update_res.json()["done"] == 1

    # Delete
    delete_res = client.delete(f"/tasks/{task_id}")
    assert delete_res.status_code == 204

    # Verify gone
    gone_res = client.get(f"/tasks/{task_id}")
    assert gone_res.status_code == 404
