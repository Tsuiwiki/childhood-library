"""Unified Media Asset Service (T-07, M0 local adapter).

Package initialisation is deliberately LAZY: importing ``app.media`` or a
single pure-Python submodule (``provider`` / ``integrity``) must not pull in
``app.models.__init__``, which registers the whole T-06 ORM and needs
SQLAlchemy. Callers that use provider value sets reuse the T-06 enums as the
single source of truth and therefore run inside the venv / container where SQLAlchemy
is pinned by requirements.lock. No vendor URL is ever produced here.
"""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "ByteRange",
    "ChecksumMismatch",
    "IntegrityResult",
    "LocalStorageAdapter",
    "MediaAccessDecision",
    "MediaAccessDenied",
    "MediaAccessInput",
    "MediaProbe",
    "ObjectKeyRejected",
    "ObjectNotFound",
    "ObjectStat",
    "ObjectTooLarge",
    "StorageError",
    "StorageProvider",
    "StorageReadOnly",
    "evaluate_media_access",
    "probe_file",
    "require_internal_content",
    "require_public_url",
    "sha256_path",
    "sha256_stream",
    "verify_manifest",
    "verify_object",
]

_LAZY: dict[str, str] = {
    "ByteRange": "app.media.provider",
    "ChecksumMismatch": "app.media.provider",
    "ObjectKeyRejected": "app.media.provider",
    "ObjectNotFound": "app.media.provider",
    "ObjectStat": "app.media.provider",
    "ObjectTooLarge": "app.media.provider",
    "StorageError": "app.media.provider",
    "StorageProvider": "app.media.provider",
    "StorageReadOnly": "app.media.provider",
    "IntegrityResult": "app.media.integrity",
    "sha256_path": "app.media.integrity",
    "sha256_stream": "app.media.integrity",
    "verify_manifest": "app.media.integrity",
    "verify_object": "app.media.integrity",
    "LocalStorageAdapter": "app.media.local",
    "MediaProbe": "app.media.probe",
    "probe_file": "app.media.probe",
    "MediaAccessDecision": "app.media.rights_gate",
    "MediaAccessDenied": "app.media.rights_gate",
    "MediaAccessInput": "app.media.rights_gate",
    "evaluate_media_access": "app.media.rights_gate",
    "require_internal_content": "app.media.rights_gate",
    "require_public_url": "app.media.rights_gate",
}


def __getattr__(name: str) -> Any:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
    value = getattr(import_module(module), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
