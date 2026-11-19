"""T-07 provider round-trip: put / get / stat / delete / range / checksum."""
from __future__ import annotations

import hashlib

import pytest

from app.media.local import LocalStorageAdapter
from app.media.provider import (
    ChecksumMismatch,
    ObjectKeyRejected,
    ObjectNotFound,
    ObjectTooLarge,
    StorageReadOnly,
)

KEY = "childhood-library/audio/music/general/probe.wav"
PAYLOAD = b"RIFF-fake-audio-bytes-" * 64


def test_full_round_trip(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(PAYLOAD)
    expected = hashlib.sha256(PAYLOAD).hexdigest()

    stat = provider.put(KEY, source, expected_sha256=expected)
    assert stat.object_key == KEY
    assert stat.size_bytes == len(PAYLOAD)
    assert stat.checksum_sha256 == expected

    assert provider.stat(KEY).size_bytes == len(PAYLOAD)
    assert provider.checksum(KEY) == expected
    with provider.get(KEY) as handle:
        assert handle.read() == PAYLOAD

    span, handle = provider.range(KEY, 10, 19)
    try:
        assert span.start == 10 and span.end == 19
        assert span.length == 10
        assert span.total == len(PAYLOAD)
        assert span.content_range == "bytes 10-19/%d" % len(PAYLOAD)
        assert handle.read(10) == PAYLOAD[10:20]
    finally:
        handle.close()

    assert provider.delete(KEY) is True
    assert provider.delete(KEY) is False
    with pytest.raises(ObjectNotFound):
        provider.stat(KEY)


def test_range_open_ended(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    provider.put(KEY, _bytes_io(PAYLOAD))
    span, handle = provider.range(KEY, len(PAYLOAD) - 5)
    try:
        assert span.end == len(PAYLOAD) - 1
        assert handle.read() == PAYLOAD[-5:]
    finally:
        handle.close()


def _bytes_io(data: bytes):
    from io import BytesIO

    return BytesIO(data)


@pytest.mark.parametrize(
    "key",
    [
        "",
        "/absolute/file.wav",
        "../escape.wav",
        "a/../../escape.wav",
        "a//b.wav",
        "a/./b.wav",
        "a\\b.wav",
        "a/\x00b.wav",
    ],
)
def test_object_key_sandbox(tmp_path, key):
    provider = LocalStorageAdapter(tmp_path)
    with pytest.raises(ObjectKeyRejected):
        provider._path(key)


def test_checksum_mismatch_does_not_replace_existing(tmp_path):
    provider = LocalStorageAdapter(tmp_path)
    original = tmp_path / "original.bin"
    original.write_bytes(PAYLOAD)
    provider.put(KEY, original)
    before = (tmp_path / KEY).read_bytes()

    with pytest.raises(ChecksumMismatch):
        provider.put(KEY, _bytes_io(b"different"), expected_sha256="0" * 64)
    assert (tmp_path / KEY).read_bytes() == before
    assert not list(tmp_path.rglob(".cl-upload-*"))


def test_read_only_mount_rejects_writes(tmp_path):
    provider = LocalStorageAdapter(tmp_path, read_only=True)
    with pytest.raises(StorageReadOnly):
        provider.put(KEY, _bytes_io(PAYLOAD))
    with pytest.raises(StorageReadOnly):
        provider.delete(KEY)


def test_size_ceiling(tmp_path):
    provider = LocalStorageAdapter(tmp_path, max_object_bytes=16)
    with pytest.raises(ObjectTooLarge):
        provider.put(KEY, _bytes_io(PAYLOAD))
    assert not (tmp_path / KEY).exists()
