"""Unified error envelope, error codes and request-id propagation."""


def test_not_found_envelope(client):
    response = client.get("/no-such-path")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
    assert response.headers["X-Error-Code"] == "NOT_FOUND"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_validation_error_envelope(client):
    response = client.get("/api/v1/catalog?limit=abc")
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["request_id"]
    assert body["data"]["errors"][0]["loc"] == ["query", "limit"]


def test_method_not_allowed_envelope(client):
    response = client.post("/healthz")
    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"


def test_request_id_is_propagated(client):
    response = client.get("/healthz", headers={"X-Request-ID": "test-rid-001"})
    assert response.headers["X-Request-ID"] == "test-rid-001"
    assert response.json()["request_id"] == "test-rid-001"


def test_error_response_never_leaks_tracebacks(client):
    body = client.get("/no-such-path").json()
    assert "Traceback" not in str(body)
    assert set(body) == {"code", "message", "data", "request_id"}
