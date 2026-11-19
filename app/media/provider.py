"""StorageProvider contract for the unified Media Asset Service.

Source: MEDIA_ASSET_DESIGN.md section 3 / 8 / 10 (M0) and
IMPLEMENTATION_ROADMAP.md T-07.

The provider owns ONLY byte-level operations. Rights, publication and checksum
policy live in ``rights_gate.py`` / ``service.py``. ``object_key`` is a
provider-neutral key, never a vendor URL: adding a COS / BOS / S3 adapter must
not require changing callers or database rows.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


class StorageError(Exception):
    """Base class for provider failures."""


class ObjectNotFound(StorageError):
    """Requested object_key has no stored object."""


class ObjectKeyRejected(StorageError):
    """object_key is absolute, traverses outside the root, or is malformed."""


class StorageReadOnly(StorageError):
    """A write was attempted on a read-only mount (e.g. the api container)."""


class ObjectTooLarge(StorageError):
    """Object exceeds the configured size ceiling."""


class ChecksumMismatch(StorageError):
    """Stored bytes do not match the declared SHA-256."""


@dataclass(frozen=True)
class ObjectStat:
    object_key: str
    size_bytes: int
    checksum_sha256: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class ByteRange:
    start: int
    end: int  # inclusive
    total: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1

    @property
    def content_range(self) -> str:
        return "bytes %d-%d/%d" % (self.start, self.end, self.total)


class StorageProvider(ABC):
    """put / get / stat / delete / range / checksum.

    ``get`` and ``range`` return an open binary handle; the CALLER closes it.
    Implementations must not emit or persist vendor URLs.
    """

    name: str = "abstract"

    @abstractmethod
    def put(
        self,
        object_key: str,
        source: BinaryIO | Path,
        *,
        expected_sha256: str | None = None,
    ) -> ObjectStat:
        """Store bytes atomically; optionally assert a declared checksum."""

    @abstractmethod
    def get(self, object_key: str) -> BinaryIO:
        """Open the whole object for reading."""

    @abstractmethod
    def stat(self, object_key: str) -> ObjectStat:
        """Return size / checksum / mime metadata without reading the body."""

    @abstractmethod
    def delete(self, object_key: str) -> bool:
        """Remove one object. Returns False when it did not exist."""

    @abstractmethod
    def range(
        self, object_key: str, start: int, end: int | None = None
    ) -> tuple[ByteRange, BinaryIO]:
        """Return an inclusive byte range and a handle positioned at ``start``."""

    @abstractmethod
    def checksum(self, object_key: str) -> str:
        """Recompute SHA-256 from the stored bytes."""
