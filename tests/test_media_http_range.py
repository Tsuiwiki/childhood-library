"""T-07 Range playback adapter: 200 / 206 / 416 and the access gate."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.errors import AppError, ErrorCode
from app.media.http import RangeNotSatisfiable, build_media_response, parse_range
from app.media.local import LocalStorageAdapter
from app.media.rights_gate import MediaAccessInput, evaluate_media_access

KEY = "childhood-library/audio/music/general/range.wav"
PAYLOAD = bytes(range(256)) * 4
ALLOWED = evaluate_media_access(MediaAccessInput(checksum_sha256="a" * 64))
DENIED = evaluate_media_access(
    MediaAccessInput(checksum_sha256="a" * 64, integrity_ok=False)
)


def _client(provider, decision):
    app = FastAPI()

    @app.get("/asset")
    def asset(request: Request):
        return build_media_response(
            provider,
            KEY,
            decision=decision,
            range_header=request.headers.get("range"),
            mime_type="audio/wav",
        )

    return TestClient(app)


@pytest.fixture
def provider(tmp_path):
    store = LocalStorageAdapter(tmp_path)
    source = tmp_path / "src.bin"
    source.write_bytes(PAYLOAD)
    store.put(KEY, source)
    return store


def test_parse_range_forms():
    total = len(PAYLOAD)
    assert parse_range(None, total) is None
    assert parse_range("bytes=0-9", total) == (0, 9)
    assert parse_range("bytes=10-", total) == (10, total - 1)
    assert parse_range("bytes=-5", total) == (total - 5, total - 1)
    assert parse_range("bytes=0-", total) == (0, total - 1)
    with pytest.raises(RangeNotSatisfiable):
        parse_range("bytes=abc", total)
    with pytest.raises(RangeNotSatisfiable):
        parse_range("bytes=999999-", total)
    with pytest.raises(RangeNotSatisfiable):
        parse_range("bytes=0-1", 0)


def test_full_body(provider):
    response = _client(provider, ALLOWED).get("/asset")
    assert response.status_code == 200
    assert response.content == PAYLOAD
    assert response.headers["Accept-Ranges"] == "bytes"
    assert response.headers["Content-Type"].startswith("audio/wav")
    assert int(response.headers["Content-Length"]) == len(PAYLOAD)


def test_partial_content(provider):
    response = _client(provider, ALLOWED).get("/asset", headers={"Range": "bytes=0-9"})
    assert response.status_code == 206
    assert response.content == PAYLOAD[:10]
    assert response.headers["Content-Range"] == "bytes 0-9/%d" % len(PAYLOAD)
    assert int(response.headers["Content-Length"]) == 10


def test_suffix_range(provider):
    response = _client(provider, ALLOWED).get("/asset", headers={"Range": "bytes=-5"})
    assert response.status_code == 206
    assert response.content == PAYLOAD[-5:]


def test_unsatisfiable_range(provider):
    response = _client(provider, ALLOWED).get(
        "/asset", headers={"Range": "bytes=999999-"}
    )
    assert response.status_code == 416
    assert response.headers["Content-Range"] == "bytes */%d" % len(PAYLOAD)


def test_denied_decision_raises_forbidden(provider):
    with pytest.raises(AppError) as exc:
        build_media_response(provider, KEY, decision=DENIED)
    assert exc.value.code == ErrorCode.FORBIDDEN
    assert exc.value.status == 403
