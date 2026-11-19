"""Structured logging contract."""
import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_fields():
    record = logging.LogRecord(
        name="app.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )
    record.status_code = 200
    record.duration_ms = 1.23
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "INFO"
    assert payload["message"] == "request completed"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 1.23
    assert "request_id" in payload
    assert "ts" in payload
    assert "logger" in payload


def test_access_log_has_request_id_and_status(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.access"):
        response = client.get("/healthz")
    assert response.status_code == 200
    records = [record for record in caplog.records if record.name == "app.access"]
    assert records
    record = records[-1]
    assert record.status_code == 200
    assert record.request_id == response.headers["X-Request-ID"]
    assert record.method == "GET"
    assert record.path == "/healthz"
    assert record.duration_ms >= 0


def test_error_log_carries_error_code(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.access"):
        client.get("/api/v1/catalog")
    records = [record for record in caplog.records if record.name == "app.access"]
    assert records[-1].error_code == "NOT_IMPLEMENTED"
    assert records[-1].status_code == 501
