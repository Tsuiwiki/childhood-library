"""T-07 capability endpoint is observable; the domain list stays a placeholder."""
from __future__ import annotations

import json


def test_capabilities_endpoint(client):
    response = client.get("/api/v1/media/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "OK"
    data = body["data"]
    assert data["stage"] == "T-07 / M0 local adapter"
    assert data["provider"] == "local"
    assert data["public_url_issued"] is False
    assert data["operations"] == [
        "put",
        "get",
        "stat",
        "delete",
        "range",
        "checksum",
    ]
    assert data["rights_gate"] == [
        "research_metadata",
        "internal_content",
        "public_url",
    ]
    # No access URL is ever emitted by this endpoint.
    assert "://" not in json.dumps(data, ensure_ascii=False)
    assert isinstance(data["root_exists"], bool)
    assert isinstance(data["read_only"], bool)
    assert data["flat_object_count"] >= 0


def test_domain_list_is_still_a_placeholder(client):
    response = client.get("/api/v1/media")
    assert response.status_code == 501
    assert response.json()["code"] == "NOT_IMPLEMENTED"


def test_placeholder_pagination_still_validated(client):
    assert client.get("/api/v1/media?limit=0").status_code == 422
    assert client.get("/api/v1/media?limit=101").status_code == 422
