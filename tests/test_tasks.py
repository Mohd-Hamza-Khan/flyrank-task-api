"""Tests for the FlyRank Task CRUD API.

Uses FastAPI's TestClient (httpx-backed) so no external server is needed.
Each test gets a fresh in-memory TaskService via an autouse fixture.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.task import TaskCreate
from app.services.task_service import TaskService, get_task_service


@pytest.fixture
def service() -> TaskService:
    """A fresh TaskService instance, shared between the app and the test."""
    return TaskService()


@pytest.fixture
def fastapi_app(service: TaskService) -> FastAPI:
    """A FastAPI app with the shared TaskService injected via dependency override."""
    app = create_app()
    app.dependency_overrides[get_task_service] = lambda: service
    return app


@pytest.fixture
def client(fastapi_app: FastAPI) -> TestClient:
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


def test_list_tasks_empty(client: TestClient):
    """GET /tasks returns 200 and an empty list when no tasks exist."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_non_empty(client: TestClient, service: TaskService):
    """GET /tasks returns 200 and all stored tasks."""
    service.create_task(TaskCreate(title="Task A"))
    service.create_task(TaskCreate(title="Task B"))

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task A"
    assert data[1]["title"] == "Task B"


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------


def test_get_task_existing(client: TestClient, service: TaskService):
    """GET /tasks/{id} returns 200 for a valid ID."""
    task = service.create_task(TaskCreate(title="My Task"))

    response = client.get(f"/tasks/{task.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == task.id
    assert result["title"] == "My Task"
    assert result["status"] == "todo"
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
    """POST /tasks with only required fields returns 201."""
    response = client.post("/tasks", json={"title": "Simple Task"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Simple Task"
    assert task["description"] is None
    assert task["status"] == "todo"
    assert task["id"] == 1
    assert "created_at" in task


def test_create_task_full(client: TestClient):
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


def test_update_task_existing(client: TestClient, service: TaskService):
    """PUT /tasks/{id} returns 200 and updated fields."""
    task = service.create_task(TaskCreate(title="Original"))

    response = client.put(
        f"/tasks/{task.id}",
        json={"title": "Updated", "description": "New desc", "status": "done"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == task.id
    assert result["title"] == "Updated"
    assert result["description"] == "New desc"
    assert result["status"] == "done"


def test_update_task_not_found(client: TestClient):
    """PUT /tasks/{id} returns 404 for an unknown ID."""
    response = client.put(
        "/tasks/999",
        json={"title": "Updated"},
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_task_invalid_body(client: TestClient, service: TaskService):
    """PUT /tasks/{id} with an invalid body returns 400."""
    task = service.create_task(TaskCreate(title="Original"))

    response = client.put(f"/tasks/{task.id}", json={})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------


def test_delete_task_existing(client: TestClient, service: TaskService):
    """DELETE /tasks/{id} returns 204 with an empty body."""
    task = service.create_task(TaskCreate(title="To Delete"))

    response = client.delete(f"/tasks/{task.id}")
    assert response.status_code == 204
    assert response.content == b""

    # Confirm the task is gone
    follow_up = client.get(f"/tasks/{task.id}")
    assert follow_up.status_code == 404


def test_delete_task_not_found(client: TestClient):
    """DELETE /tasks/{id} returns 404 for an unknown ID."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# Full lifecycle
# ---------------------------------------------------------------------------


def test_full_lifecycle(client: TestClient, service: TaskService):
    """Create, read, update, delete, verify gone — one task end-to-end."""
    # Create (via API to exercise the full path)
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
