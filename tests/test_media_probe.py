"""T-07 signature-first format / best-effort duration probing."""
from __future__ import annotations

import wave

from app.media.probe import probe_file
from app.models.enums import MediaType


def _wav(path, frames=8000, rate=8000):
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(b"\x00\x00" * frames)
    return path


def test_wav_signature_and_duration(tmp_path):
    probe = probe_file(_wav(tmp_path / "tone.wav"))
    assert probe.mime_type == "audio/wav"
    assert probe.file_extension == ".wav"
    assert probe.media_type == MediaType.AUDIO.value
    assert probe.duration_ms == 1000
    assert probe.duration_probe == "wav_header"


def test_mp3_signature_without_extension_trust(tmp_path):
    # Named .wav but actually ID3: the signature wins over the extension.
    bad_name = tmp_path / "disguised.wav"
    bad_name.write_bytes(b"ID3\x04\x00\x00" + b"\x00" * 64)
    probe = probe_file(bad_name)
    assert probe.mime_type == "audio/mpeg"
    assert probe.file_extension == ".mp3"
    assert probe.media_type == MediaType.AUDIO.value


def test_isobmff_variants(tmp_path):
    head = b"\x00\x00\x00\x18ftypM4A " + b"\x00" * 8
    m4a = tmp_path / "clip.m4a"
    m4a.write_bytes(head)
    assert probe_file(m4a).mime_type == "audio/mp4"
    mp4 = tmp_path / "clip.mp4"
    mp4.write_bytes(head)
    assert probe_file(mp4).mime_type == "video/mp4"
    assert probe_file(mp4).media_type == MediaType.VIDEO.value


def test_score_xml_and_unknown_signature(tmp_path):
    score = tmp_path / "score.musicxml"
    score.write_bytes(b'<?xml version="1.0"?><score-partwise version="4.0"></score-partwise>')
    probe = probe_file(score)
    assert probe.file_extension == ".musicxml"
    assert probe.media_type == MediaType.SCORE_XML.value

    unknown = tmp_path / "mystery.bin"
    unknown.write_bytes(b"this is not a recognised container")
    probe = probe_file(unknown)
    assert probe.mime_type is None
    assert probe.media_type == MediaType.OTHER.value


def test_duration_override_is_recorded_as_provided(tmp_path):
    probe = probe_file(_wav(tmp_path / "tone.wav"), duration_ms_override=4321)
    assert probe.duration_ms == 4321
    assert probe.duration_probe == "provided"


def test_missing_file_never_raises(tmp_path):
    probe = probe_file(tmp_path / "does-not-exist.mp3")
    assert probe.mime_type is None
    assert probe.duration_ms is None
