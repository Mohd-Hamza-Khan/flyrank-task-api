"""Core configuration."""

import os
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables with sensible defaults."""

    PROJECT_NAME: str = "FlyRank Task CRUD API"
    VERSION: str = "2.0.0"
    DB_PATH: str = os.getenv(
        "DB_PATH", str(Path(__file__).resolve().parent.parent.parent / "tasks.db")
    )


settings = Settings()
