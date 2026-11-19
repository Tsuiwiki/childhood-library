"""All seven domains are registered but explicitly not implemented yet."""
import pytest

from app.api.v1.router import DOMAIN_NAMES

EXPECTED_DOMAINS = (
    "catalog",
    "versions",
    "sources",
    "rights",
    "reviews",
    "media",
    "ingestion",
)


def test_all_domains_registered():
    assert DOMAIN_NAMES == EXPECTED_DOMAINS


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
def test_domain_returns_not_implemented(client, domain):
    response = client.get(f"/api/v1/{domain}")
    assert response.status_code == 501
    body = response.json()
    assert body["code"] == "NOT_IMPLEMENTED"
    assert body["data"]["domain"] == domain
    assert body["data"]["planned_from"] == "post-T-06"
    assert response.headers["X-Error-Code"] == "NOT_IMPLEMENTED"


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
def test_domain_pagination_is_validated(client, domain):
    assert client.get(f"/api/v1/{domain}?limit=0").status_code == 422
    assert client.get(f"/api/v1/{domain}?limit=101").status_code == 422


def test_openapi_contains_all_domains(client):
    spec = client.get("/api/openapi.json").json()
    for domain in EXPECTED_DOMAINS:
        assert f"/api/v1/{domain}" in spec["paths"]
    assert "/healthz" in spec["paths"]
