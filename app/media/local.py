"""LocalStorageAdapter - M0 provider (MEDIA_ASSET_DESIGN.md section 10 / 13).

Sandbox rules:
* every object_key is a relative POSIX path, resolved and checked against root;
* writes are atomic (temp file in the same directory + os.replace);
* a read-only mount rejects put/delete explicitly, so the api container cannot
  mutate the migrated flat media even when it can read them;
* put verifies a declared SHA-256 BEFORE replacing any existing object.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from app.media.integrity import CHUNK_SIZE, sha256_stream
from app.media.provider import (
    ByteRange,
    ChecksumMismatch,
    ObjectKeyRejected,
    ObjectNotFound,
    ObjectStat,
    ObjectTooLarge,
    StorageProvider,
    StorageReadOnly,
)
from app.models.enums import StorageProvider as StorageProviderEnum


class LocalStorageAdapter(StorageProvider):
    name = StorageProviderEnum.LOCAL.value

    def __init__(
        self,
        root: Path | str,
        *,
        read_only: bool = False,
        max_object_bytes: int = 256 * 1024 * 1024,
    ) -> None:
        self.root = Path(root).resolve()
        self.read_only = bool(read_only)
        self.max_object_bytes = int(max_object_bytes)

    def __repr__(self) -> str:
        return "LocalStorageAdapter(root=%s, read_only=%s)" % (
            self.root,
            self.read_only,
        )

    def _path(self, object_key: str) -> Path:
        key = (object_key or "").strip()
        if not key or "\x00" in key or "\\" in key or key.startswith("/"):
            raise ObjectKeyRejected("invalid object_key: %r" % object_key)
        normalised = PurePosixPath(key)
        if key != str(normalised) or ".." in normalised.parts:
            raise ObjectKeyRejected("object_key must be canonical: %r" % object_key)
        target = (self.root / key).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ObjectKeyRejected("object_key escapes the storage root") from exc
        return target

    def put(
        self,
        object_key: str,
        source: BinaryIO | Path,
        *,
        expected_sha256: str | None = None,
    ) -> ObjectStat:
        if self.read_only:
            raise StorageReadOnly("this provider is mounted read-only")
        target = self._path(object_key)
        target.parent.mkdir(parents=True, exist_ok=True)

        handle: BinaryIO
        close_after = False
        if isinstance(source, (str, Path)):
            handle = Path(source).open("rb")
            close_after = True
        else:
            handle = source

        tmp_path: str | None = None
        try:
            fd, tmp_path = tempfile.mkstemp(
                prefix=".cl-upload-", dir=str(target.parent)
            )
            digest_bytes = 0
            with os.fdopen(fd, "wb") as out:
                for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
                    digest_bytes += len(chunk)
                    if digest_bytes > self.max_object_bytes:
                        raise ObjectTooLarge(
                            "object exceeds %d bytes" % self.max_object_bytes
                        )
                    out.write(chunk)
            if close_after:
                handle.close()

            with open(tmp_path, "rb") as staged:
                actual = sha256_stream(staged)
            if expected_sha256 and actual != expected_sha256:
                raise ChecksumMismatch(
                    "declared %s but stored %s" % (expected_sha256, actual)
                )
            os.replace(tmp_path, target)
            tmp_path = None
            return ObjectStat(
                object_key=object_key,
                size_bytes=target.stat().st_size,
                checksum_sha256=actual,
            )
        finally:
            if close_after and not handle.closed:
                handle.close()
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except FileNotFoundError:
                    pass

    def get(self, object_key: str) -> BinaryIO:
        target = self._path(object_key)
        if not target.is_file():
            raise ObjectNotFound(object_key)
        return target.open("rb")

    def stat(self, object_key: str) -> ObjectStat:
        target = self._path(object_key)
        if not target.is_file():
            raise ObjectNotFound(object_key)
        # checksum is deliberately NOT recomputed here; use checksum().
        return ObjectStat(object_key=object_key, size_bytes=target.stat().st_size)

    def checksum(self, object_key: str) -> str:
        with self.get(object_key) as handle:
            return sha256_stream(handle)

    def delete(self, object_key: str) -> bool:
        if self.read_only:
            raise StorageReadOnly("this provider is mounted read-only")
        target = self._path(object_key)
        if not target.is_file():
            return False
        target.unlink()
        return True

    def range(
        self, object_key: str, start: int, end: int | None = None
    ) -> tuple[ByteRange, BinaryIO]:
        target = self._path(object_key)
        if not target.is_file():
            raise ObjectNotFound(object_key)
        total = target.stat().st_size
        if start < 0 or (end is not None and end < start):
            raise ValueError("invalid byte range")
        if total and start >= total:
            raise ValueError("range start beyond end of object")
        last = total - 1 if end is None else min(end, total - 1)
        handle = target.open("rb")
        handle.seek(start)
        return ByteRange(start=start, end=last, total=total), handle
