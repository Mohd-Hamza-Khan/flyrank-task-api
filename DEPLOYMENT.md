# FlyRank Task CRUD API — Deployment & Operational Guide

This document outlines how to build, test, configure, and run the FlyRank Task CRUD API (Assignment A2 — SQLite Integration).

---

## 1. Local Development

### Prerequisites
- Python 3.10+
- pip

### Setup & Run
```bash
# Clone the repository and navigate into the project directory
cd flyrank-task-api

# Install dependencies
pip install -r requirements.txt

# Run the API server with auto-reload
uvicorn app.main:app --reload
```

Once running:
- **API Root**: http://127.0.0.1:8000
- **Interactive Swagger UI Docs**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc

---

## 2. Running Tests

The test suite covers all 7 API endpoints, database schema initialization, seed data validation, idempotency, and the full CRUD lifecycle.

```bash
pytest tests/ -v
```

To run a specific test file:
```bash
pytest tests/test_database.py -v
pytest tests/test_tasks.py -v
```

---

## 3. Configuration

Environment variables (managed via `app/core/config.py`):
- `DB_PATH`: Path to the SQLite database file (defaults to `tasks.db` in project root).

---

## 4. CI/CD Pipeline

A GitHub Actions workflow (`.github/workflows/ci.yml`) automatically triggers on push and pull requests to `main`/`master`, setting up Python 3.10 and executing the pytest test suite.
