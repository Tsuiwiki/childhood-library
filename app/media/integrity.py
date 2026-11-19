"""SHA-256 helpers and integrity reporting (MEDIA_ASSET_DESIGN.md section 9).

A mismatch is reported, never silently repaired and never auto-deleted: a human
must decide whether the object or the recorded checksum is wrong.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Protocol

from app.media.provider import ObjectNotFound

CHUNK_SIZE = 1024 * 1024


class ChecksumProvider(Protocol):
    """Minimal contract needed by verify_object (duck-typed, no DB)."""

    def checksum(self, object_key: str) -> str: ...


def sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
        digest.update(chunk)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    with Path(path).open("rb") as handle:
        return sha256_stream(handle)


@dataclass(frozen=True)
class IntegrityResult:
    object_key: str
    expected: str | None
    actual: str | None
    ok: bool
    message: str

    def as_dict(self) -> dict:
        return {
            "object_key": self.object_key,
            "expected": self.expected,
            "actual": self.actual,
            "ok": self.ok,
            "message": self.message,
        }


def verify_object(
    provider: ChecksumProvider, object_key: str, expected_sha256: str | None
) -> IntegrityResult:
    """Compare stored bytes with the checksum recorded in the database."""
    try:
        actual = provider.checksum(object_key)
    except ObjectNotFound as exc:
        return IntegrityResult(
            object_key, expected_sha256, None, False, "object missing: %s" % exc
        )
    if not expected_sha256:
        return IntegrityResult(
            object_key, None, actual, False, "no checksum recorded for this asset"
        )
    if actual != expected_sha256:
        return IntegrityResult(
            object_key,
            expected_sha256,
            actual,
            False,
            "CHECKSUM MISMATCH: stored bytes differ from the recorded SHA-256",
        )
    return IntegrityResult(object_key, expected_sha256, actual, True, "ok")


def verify_manifest(root: Path, manifest: dict[str, str]) -> list[IntegrityResult]:
    """Read-only check of flat files against a {filename: sha256} manifest.

    Used by scripts/media_integrity.py for the migrated local media. Never
    modifies, moves or deletes anything.
    """
    results: list[IntegrityResult] = []
    root = Path(root)
    for name, expected in sorted(manifest.items()):
        path = root / name
        if not path.is_file():
            results.append(
                IntegrityResult(name, expected, None, False, "file missing")
            )
            continue
        results.append(
            verify_object(_PathAdapter(root), name, expected)
        )
    return results


class _PathAdapter:
    """Tiny adapter so verify_manifest can reuse verify_object."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def checksum(self, object_key: str) -> str:
        path = self._root / object_key
        if not path.is_file():
            raise ObjectNotFound(object_key)
        return sha256_path(path)
