"""Shared fixtures. Tests must never depend on the repo-root .env."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env="testing",
        health_check_db=False,
        log_dir=None,
        log_json=True,
        log_level="INFO",
    )


@pytest.fixture(scope="session")
def client(settings):
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client
