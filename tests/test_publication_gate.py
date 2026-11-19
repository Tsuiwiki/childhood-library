"""DATABASE_DESIGN.md section 4 publication gate, five independent checks."""
from dataclasses import fields
from datetime import date

from app.domain.publication_gate import (
    GateInput,
    PendingObject,
    PlaybackCandidate,
    ReviewCandidate,
    evaluate_publication_gate,
    rights_clearance_is_valid,
)
from app.domain.status import QualityStatus


def approved_payload(**overrides):
    base = dict(
        quality_status=QualityStatus.SUITABLE.value,
        pending_objects=(
            PendingObject("work_version", "wv-1", rights_verified=True),
            PendingObject("media_asset", "ma-1", rights_verified=True),
        ),
        playback_resources=(
            PlaybackCandidate("pr-1", review_status="approved"),
        ),
        editorial_reviews=(
            ReviewCandidate("rv-1", "core", is_binding=True),
        ),
        audit_log_present=True,
    )
    base.update(overrides)
    return GateInput(**base)


def test_full_gate_passes():
    result = evaluate_publication_gate(approved_payload())
    assert result.allowed is True
    assert result.issues == ()


def test_gate_rejects_unsuitable_quality():
    result = evaluate_publication_gate(
        approved_payload(quality_status="unreviewed")
    )
    assert result.allowed is False
    assert any("quality_status" in issue for issue in result.issues)


def test_gate_rejects_unverified_rights_per_object():
    result = evaluate_publication_gate(
        approved_payload(
            pending_objects=(PendingObject("media_asset", "ma-1"),)
        )
    )
    assert result.allowed is False
    assert any("unverified rights for media_asset:ma-1" in i for i in result.issues)


def test_gate_rejects_unapproved_playback():
    result = evaluate_publication_gate(
        approved_payload(
            playback_resources=(
                PlaybackCandidate("pr-1", review_status="pending"),
            )
        )
    )
    assert result.allowed is False
    assert any("not approved" in i for i in result.issues)


def test_gate_rejects_embed_without_permission():
    result = evaluate_publication_gate(
        approved_payload(
            playback_resources=(
                PlaybackCandidate(
                    "pr-1", review_status="approved", embed_enabled=True
                ),
            )
        )
    )
    assert result.allowed is False
    assert any("embed enabled without permission" in i for i in result.issues)


def test_gate_rejects_ai_only_review():
    result = evaluate_publication_gate(
        approved_payload(
            editorial_reviews=(
                ReviewCandidate("rv-ai", "core", is_binding=False),
            )
        )
    )
    assert result.allowed is False
    assert any("binding positive editorial review" in i for i in result.issues)


def test_gate_rejects_not_recommended_review():
    result = evaluate_publication_gate(
        approved_payload(
            editorial_reviews=(
                ReviewCandidate("rv-1", "not_recommended", is_binding=True),
            )
        )
    )
    assert result.allowed is False


def test_gate_requires_audit_log():
    result = evaluate_publication_gate(approved_payload(audit_log_present=False))
    assert result.allowed is False
    assert any("audit log" in i for i in result.issues)


def test_expired_rights_clearance_is_invalid():
    assert rights_clearance_is_valid("verified", None) is True
    assert rights_clearance_is_valid(
        "verified", date(2020, 1, 1), date(2026, 11, 19)
    ) is False
    assert rights_clearance_is_valid("unknown", None) is False
    assert rights_clearance_is_valid("restricted", None) is False


def test_research_status_is_not_a_gate_input():
    names = {field.name for field in fields(GateInput)}
    assert "research_status" not in names
    assert "rights_status" not in names
