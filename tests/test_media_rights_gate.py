"""T-07 acceptance: unauthorised assets must never yield a public URL."""
from __future__ import annotations

from datetime import date

import pytest

from app.domain.status import PublicationStatus, RightsStatus
from app.media.rights_gate import (
    MediaAccessDenied,
    MediaAccessInput,
    evaluate_media_access,
    require_internal_content,
    require_public_url,
)
from app.models.enums import AccessMethod, ReviewStatus

TODAY = date(2026, 11, 19)
CHECKSUM = "a" * 64

FULLY_CLEARED = MediaAccessInput(
    checksum_sha256=CHECKSUM,
    integrity_ok=True,
    rights_status=RightsStatus.VERIFIED.value,
    publication_status=PublicationStatus.PUBLISHED.value,
    review_status=ReviewStatus.APPROVED.value,
    access_policy=AccessMethod.LICENSED_MEDIA.value,
    rights_valid_until=date(2027, 1, 1),
    today=TODAY,
)


def test_research_registration_is_never_blocked():
    decision = evaluate_media_access(
        MediaAccessInput(checksum_sha256=None, rights_status=RightsStatus.UNKNOWN.value)
    )
    assert decision.research_metadata is True
    # Rights unknown blocks public URL, not cataloguing.
    assert decision.public_url is False


def test_default_asset_does_not_get_public_url():
    decision = evaluate_media_access(
        MediaAccessInput(checksum_sha256=CHECKSUM, today=TODAY)
    )
    assert decision.internal_content is True
    assert decision.public_url is False
    assert any("verified rights" in issue for issue in decision.issues)
    with pytest.raises(MediaAccessDenied):
        require_public_url(decision)


def test_fully_cleared_asset_allows_public_url():
    decision = evaluate_media_access(FULLY_CLEARED)
    assert decision.public_url is True
    assert decision.issues == ()
    require_public_url(decision)
    require_internal_content(decision)


@pytest.mark.parametrize(
    "field,value,expected_issue",
    [
        ("rights_status", RightsStatus.UNKNOWN.value, "verified rights"),
        ("publication_status", PublicationStatus.DRAFT.value, "not 'published'"),
        ("review_status", ReviewStatus.PENDING.value, "not approved"),
        ("access_policy", AccessMethod.NONE.value, "access_policy is 'none'"),
        ("integrity_ok", False, "integrity check failed"),
        ("checksum_sha256", None, "checksum_sha256 is missing"),
    ],
)
def test_each_public_gate_condition_blocks(field, value, expected_issue):
    payload = MediaAccessInput(**{**FULLY_CLEARED.__dict__, field: value})
    decision = evaluate_media_access(payload)
    assert decision.public_url is False
    assert any(expected_issue in issue for issue in decision.issues), decision.issues


def test_expired_clearance_blocks_public_url():
    payload = MediaAccessInput(
        **{**FULLY_CLEARED.__dict__, "rights_valid_until": date(2026, 1, 1)}
    )
    decision = evaluate_media_access(payload)
    assert decision.public_url is False


def test_embed_requires_its_own_permission():
    payload = MediaAccessInput(
        **{**FULLY_CLEARED.__dict__, "embed_enabled": True, "embed_allowed": False}
    )
    decision = evaluate_media_access(payload)
    assert decision.public_url is False
    assert any("embed enabled without permission" in i for i in decision.issues)


def test_revoked_or_withdrawn_also_blocks_internal_content():
    revoked = evaluate_media_access(
        MediaAccessInput(
            **{**FULLY_CLEARED.__dict__, "rights_status": RightsStatus.REVOKED.value}
        )
    )
    assert revoked.internal_content is False
    assert revoked.public_url is False
    with pytest.raises(MediaAccessDenied):
        require_internal_content(revoked)

    withdrawn = evaluate_media_access(
        MediaAccessInput(
            **{
                **FULLY_CLEARED.__dict__,
                "publication_status": PublicationStatus.WITHDRAWN.value,
            }
        )
    )
    assert withdrawn.internal_content is False
