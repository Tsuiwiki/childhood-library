"""Liveness probe contract."""


def test_healthz_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "OK"
    assert body["message"] == "success"
    assert body["request_id"]
    assert response.headers["X-Request-ID"] == body["request_id"]
    data = body["data"]
    assert data["status"] == "ok"
    assert data["environment"] == "testing"
    assert data["checks"]["database_tcp"] == "disabled"
    assert data["python_version"].startswith("3.12")
    assert len(data["domains"]) == 7


def test_root_meta(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "OK"
    assert body["data"]["api_prefix"] == "/api/v1"
    assert body["data"]["docs_url"] == "/api/docs"
