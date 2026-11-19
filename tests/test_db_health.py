"""T-06 liveness / readiness contracts."""
from app.db import probe_sql


def test_healthz_reports_sql_state(client):
    body = client.get("/healthz").json()
    checks = body["data"]["checks"]
    assert checks["database_tcp"] == "disabled"
    assert checks["database_sql"] == "disabled"


def test_probe_sql_without_url():
    assert probe_sql(None) == "not_configured"


def test_readyz_not_ready_when_sql_check_disabled(client):
    response = client.get("/readyz")
    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "NOT_READY"
    assert body["data"]["ready"] is False
    assert body["data"]["checks"]["database_sql"] == "disabled"
    assert response.headers["X-Error-Code"] == "NOT_READY"


def test_readyz_ready_when_sql_probe_succeeds(monkeypatch):
    from fastapi.testclient import TestClient

    import app.api.v1.health as health_module
    from app.core.config import Settings
    from app.main import create_app

    monkeypatch.setattr(health_module, "probe_sql", lambda *a, **k: "reachable")
    settings = Settings(
        _env_file=None,
        app_env="testing",
        health_check_db=False,
        health_check_sql=True,
        database_url=None,
        log_dir=None,
    )
    with TestClient(create_app(settings)) as probe_client:
        response = probe_client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["data"]["ready"] is True
        assert response.json()["data"]["checks"]["database_sql"] == "reachable"


def test_healthz_never_contains_connection_string(client):
    body = str(client.get("/healthz").json())
    assert "postgresql" not in body
    assert "DATABASE_URL" not in body
