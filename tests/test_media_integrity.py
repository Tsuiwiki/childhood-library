"""T-07 checksum verification: drift is reported, never repaired or deleted."""
from __future__ import annotations

import hashlib

from app.media.integrity import sha256_path, verify_manifest, verify_object
from app.media.local import LocalStorageAdapter

KEY = "childhood-library/audio/music/general/check.wav"
PAYLOAD = b"checksum-fixture-bytes" * 8


def test_verify_ok(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    source = tmp_path / "src.bin"
    source.write_bytes(PAYLOAD)
    expected = hashlib.sha256(PAYLOAD).hexdigest()
    provider.put(KEY, source, expected_sha256=expected)
    result = verify_object(provider, KEY, expected)
    assert result.ok is True
    assert result.actual == expected
    assert result.message == "ok"


def test_checksum_mismatch_is_reported(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    source = tmp_path / "src.bin"
    source.write_bytes(PAYLOAD)
    provider.put(KEY, source)
    (tmp_path / KEY).write_bytes(b"tampered bytes")
    result = verify_object(provider, KEY, hashlib.sha256(PAYLOAD).hexdigest())
    assert result.ok is False
    assert "CHECKSUM MISMATCH" in result.message
    assert result.actual != result.expected
    # The object is left in place for a human decision.
    assert (tmp_path / KEY).is_file()


def test_missing_object_and_missing_checksum(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    missing = verify_object(provider, KEY, "a" * 64)
    assert missing.ok is False and missing.actual is None
    assert "missing" in missing.message

    source = tmp_path / "src.bin"
    source.write_bytes(PAYLOAD)
    provider.put(KEY, source)
    no_checksum = verify_object(provider, KEY, None)
    assert no_checksum.ok is False
    assert "no checksum recorded" in no_checksum.message


def test_manifest_check_reports_extras_without_deleting(tmp_path):
    root = tmp_path / "media"
    root.mkdir()
    good = root / "good.wav"
    good.write_bytes(PAYLOAD)
    (root / "extra.wav").write_bytes(b"orphan")
    manifest = {
        "good.wav": sha256_path(good),
        "lost.wav": "b" * 64,
        "extra.wav": "c" * 64,
    }
    results = verify_manifest(root, manifest)
    by_key = {item.object_key: item for item in results}
    assert by_key["good.wav"].ok is True
    assert "missing" in by_key["lost.wav"].message
    assert "CHECKSUM MISMATCH" in by_key["extra.wav"].message
    assert (root / "extra.wav").is_file()
