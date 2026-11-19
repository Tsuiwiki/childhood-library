"""Best-effort media format / duration probe.

Two rules from MEDIA_ASSET_DESIGN.md section 9 and scripts/asset_inventory.py
L37-L57 are preserved here:

* MIME is derived from FILE SIGNATURES, not from a client-supplied Content-Type
  or a trusted extension. The extension only refines containers that genuinely
  share a signature (m4a / mp4 both start with ftyp).
* Duration uses the standard library for WAV and optional PyAV for other
  containers. With no decoder available it stays ``None`` - never guessed, never
  inferred from bitrate. Callers may supply a measured value explicitly.
"""
from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path

from app.models.enums import MediaType

HEAD_BYTES = 512


@dataclass(frozen=True)
class MediaProbe:
    mime_type: str | None
    file_extension: str | None
    media_type: str
    duration_ms: int | None
    duration_probe: str
    width: int | None = None
    height: int | None = None

    def as_dict(self) -> dict:
        return {
            "mime_type": self.mime_type,
            "file_extension": self.file_extension,
            "media_type": self.media_type,
            "duration_ms": self.duration_ms,
            "duration_probe": self.duration_probe,
            "width": self.width,
            "height": self.height,
        }


def _signature(head: bytes, suffix: str) -> tuple[str | None, str | None, str]:
    if head.startswith(b"ID3") or (
        len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0
    ):
        return "audio/mpeg", ".mp3", MediaType.AUDIO.value
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav", ".wav", MediaType.AUDIO.value
    if head[:4] == b"fLaC":
        return "audio/flac", ".flac", MediaType.AUDIO.value
    if head[:4] == b"OggS":
        return "audio/ogg", ".ogg", MediaType.AUDIO.value
    if head[4:8] == b"ftyp":
        # Both are ISO-BMFF; the extension only labels the container.
        if suffix == ".m4a":
            return "audio/mp4", ".m4a", MediaType.AUDIO.value
        return "video/mp4", ".mp4", MediaType.VIDEO.value
    if head[:4] == b"%PDF":
        return "application/pdf", ".pdf", MediaType.DOCUMENT.value
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png", ".png", MediaType.IMAGE.value
    if head[:3] == b"\xff\xd8\xff":
        return "image/jpeg", ".jpg", MediaType.IMAGE.value
    lowered = head.lower()
    if b"<svg" in lowered[:256]:
        return "image/svg+xml", ".svg", MediaType.IMAGE.value
    if b"score-partwise" in lowered or b"score-timewise" in lowered:
        return (
            "application/vnd.recordare.musicxml+xml",
            ".musicxml",
            MediaType.SCORE_XML.value,
        )
    return None, suffix or None, MediaType.OTHER.value


def _duration_ms(path: Path, suffix: str) -> tuple[int | None, str]:
    if suffix == ".wav":
        try:
            with wave.open(str(path), "rb") as wav:
                rate = wav.getframerate()
                if rate:
                    return (
                        int(round(wav.getnframes() / float(rate) * 1000)),
                        "wav_header",
                    )
        except Exception:
            pass
    try:
        import av  # optional; mirrors scripts/asset_inventory.py
    except ImportError:
        return None, "unavailable"
    try:
        with av.open(str(path)) as container:
            if container.duration:
                return int(round(container.duration / 1000)), "pyav"
            for stream in container.streams.audio:
                if stream.duration and stream.time_base:
                    seconds = float(stream.duration * stream.time_base)
                    return int(round(seconds * 1000)), "pyav"
    except Exception:
        pass
    return None, "unavailable"


def probe_file(
    path: Path, *, duration_ms_override: int | None = None
) -> MediaProbe:
    """Inspect a local file. Never raises on unreadable/partial media."""
    path = Path(path)
    suffix = path.suffix.lower()
    try:
        with path.open("rb") as handle:
            head = handle.read(HEAD_BYTES)
    except OSError:
        head = b""

    mime_type, extension, media_type = _signature(head, suffix)
    if duration_ms_override is not None:
        duration_ms, source = int(duration_ms_override), "provided"
    else:
        duration_ms, source = _duration_ms(path, suffix)

    return MediaProbe(
        mime_type=mime_type,
        file_extension=extension,
        media_type=media_type,
        duration_ms=duration_ms,
        duration_probe=source,
    )
