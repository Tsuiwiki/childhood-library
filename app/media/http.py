"""Authorised, byte-range capable media responses (MEDIA_ASSET_DESIGN.md 8).

This is the reusable HTTP adapter for T-09 / T-10: it serves BYTES from a
StorageProvider, never a vendor URL, and always checks the access decision
first. ``public_url`` stays a decision in rights_gate.py - no signed address is
generated here in T-07.
"""
from __future__ import annotations

import re
from typing import BinaryIO, Iterator

from starlette.responses import Response, StreamingResponse

from app.core.errors import AppError, ErrorCode
from app.media.provider import StorageProvider
from app.media.rights_gate import (
    MediaAccessDecision,
    MediaAccessDenied,
    require_internal_content,
)

RANGE_HEADER = re.compile(r"^bytes=(\d*)-(\d*)$")
DEFAULT_CHUNK = 64 * 1024


class RangeNotSatisfiable(Exception):
    def __init__(self, total: int) -> None:
        self.total = total
        super().__init__("range not satisfiable for %d bytes" % total)


def parse_range(header: str | None, total: int) -> tuple[int, int] | None:
    """Return inclusive (start, end); None means a full-body request."""
    if not header:
        return None
    match = RANGE_HEADER.match(header.strip())
    if not match:
        raise RangeNotSatisfiable(total)
    first, last = match.group(1), match.group(2)
    if first == "":
        if last == "" or int(last) == 0:
            raise RangeNotSatisfiable(total)
        start, end = max(0, total - int(last)), total - 1
    else:
        start = int(first)
        end = min(int(last), total - 1) if last else total - 1
    if total == 0 or start >= total or start > end:
        raise RangeNotSatisfiable(total)
    return start, end


def _iter_bytes(handle: BinaryIO, length: int, chunk_size: int) -> Iterator[bytes]:
    try:
        remaining = length
        while remaining > 0:
            chunk = handle.read(min(chunk_size, remaining))
            if not chunk:
                break
            yield chunk
            remaining -= len(chunk)
    finally:
        handle.close()


def build_media_response(
    provider: StorageProvider,
    object_key: str,
    *,
    decision: MediaAccessDecision,
    range_header: str | None = None,
    mime_type: str = "application/octet-stream",
    chunk_size: int = DEFAULT_CHUNK,
) -> Response:
    """Serve an internal, integrity-checked object with HTTP Range support."""
    try:
        require_internal_content(decision)
    except MediaAccessDenied as exc:
        raise AppError(
            ErrorCode.FORBIDDEN,
            details={"object_key": object_key, "reason": str(exc)},
        ) from exc

    stat = provider.stat(object_key)
    try:
        span = parse_range(range_header, stat.size_bytes)
    except RangeNotSatisfiable as exc:
        return Response(
            status_code=416,
            headers={
                "Content-Range": "bytes */%d" % exc.total,
                "Content-Length": "0",
            },
        )

    headers = {
        "Content-Type": mime_type,
        "Accept-Ranges": "bytes",
        "X-Content-Type-Options": "nosniff",
    }
    if stat.size_bytes == 0:
        headers["Content-Length"] = "0"
        return Response(status_code=200, content=b"", headers=headers)

    start, end = span if span else (0, stat.size_bytes - 1)
    length = end - start + 1
    _, handle = provider.range(object_key, start, end)

    headers["Content-Length"] = str(length)
    status = 200
    if span:
        status = 206
        headers["Content-Range"] = "bytes %d-%d/%d" % (start, end, stat.size_bytes)
    return StreamingResponse(
        _iter_bytes(handle, length, chunk_size),
        status_code=status,
        headers=headers,
    )
