"""object_key stays a provider-neutral internal key, never a vendor URL."""
from __future__ import annotations

import uuid

import pytest

pytest.importorskip("sqlalchemy")

from app.media.probe import MediaProbe  # noqa: E402
from app.media.service import MediaAssetService  # noqa: E402


def _probe(media_type: str, extension: str) -> MediaProbe:
    return MediaProbe(
        mime_type="audio/wav",
        file_extension=extension,
        media_type=media_type,
        duration_ms=None,
        duration_probe="unavailable",
    )


def test_audio_object_key_layout():
    key = MediaAssetService.object_key_for(
        uuid.UUID("00000000-0000-0000-0000-000000000001"),
        _probe("audio", ".wav"),
        uuid.UUID("00000000-0000-0000-0000-000000000002"),
    )
    assert key == (
        "childhood-library/audio/music/"
        "00000000-0000-0000-0000-000000000002/"
        "00000000-0000-0000-0000-000000000001.wav"
    )


def test_object_key_never_contains_a_url():
    for media_type, extension in (
        ("audio", ".mp3"),
        ("image", ".png"),
        ("score_xml", ".musicxml"),
        ("video", ".mp4"),
        ("other", ".bin"),
    ):
        key = MediaAssetService.object_key_for(
            uuid.uuid4(), _probe(media_type, extension)
        )
        assert key.startswith("childhood-library/")
        assert "://" not in key
        assert "http" not in key
        assert "?" not in key and "#" not in key
        assert key.endswith(extension)


def test_general_folder_when_no_work_id():
    key = MediaAssetService.object_key_for(uuid.uuid4(), _probe("audio", ".wav"))
    assert "/general/" in key
