"""Application-layer publication gate (DATABASE_DESIGN.md section 4).

The database enforces the single-table part (quality_status must be suitable
when published). Everything that spans objects - rights records, playback
approval, editorial review, audit trail - is checked here. T-09 wires this
function into the publishing command; T-06 only provides and tests the rule.

Research status is deliberately NOT an input: rights unknown must never block
internal research registration, only publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.status import QualityStatus, RightsStatus
from app.models.enums import ReviewConclusion, ReviewStatus


def rights_clearance_is_valid(
    status: str,
    valid_until: date | None = None,
    today: date | None = None,
) -> bool:
    """A verified clearance that has expired is not a clearance."""
    if status != RightsStatus.VERIFIED.value:
        return False
    if valid_until is not None and valid_until < (today or date.today()):
        return False
    return True


@dataclass(frozen=True)
class PendingObject:
    object_type: str
    object_id: str
    rights_verified: bool = False


@dataclass(frozen=True)
class PlaybackCandidate:
    resource_id: str
    review_status: str = ReviewStatus.PENDING.value
    embed_allowed: bool = False
    embed_enabled: bool = False


@dataclass(frozen=True)
class ReviewCandidate:
    review_id: str
    conclusion: str
    is_binding: bool = True


@dataclass(frozen=True)
class GateInput:
    quality_status: str
    pending_objects: tuple[PendingObject, ...] = ()
    playback_resources: tuple[PlaybackCandidate, ...] = ()
    editorial_reviews: tuple[ReviewCandidate, ...] = ()
    audit_log_present: bool = False


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    issues: tuple[str, ...]


def evaluate_publication_gate(payload: GateInput) -> GateResult:
    issues: list[str] = []

    # 1. Aesthetic / quality gate.
    if payload.quality_status != QualityStatus.SUITABLE.value:
        issues.append("quality_status must be 'suitable'")

    # 2. Every object that would become public needs a live verified clearance.
    for obj in payload.pending_objects:
        if not obj.rights_verified:
            issues.append(
                "unverified rights for %s:%s" % (obj.object_type, obj.object_id)
            )

    # 3. Playback entries must be approved; embedding needs its own permission.
    if not payload.playback_resources:
        issues.append("no playback resource approved for publication")
    for resource in payload.playback_resources:
        if resource.review_status != ReviewStatus.APPROVED.value:
            issues.append(
                "playback resource %s is not approved" % resource.resource_id
            )
        if resource.embed_enabled and not resource.embed_allowed:
            issues.append(
                "embed enabled without permission on %s" % resource.resource_id
            )

    # 4. A binding, positive editorial review must exist. AI suggestions do not
    #    count (PROJECT_PRINCIPLES.md: AI only advises).
    binding = [review for review in payload.editorial_reviews if review.is_binding]
    positive = [
        review
        for review in binding
        if review.conclusion != ReviewConclusion.NOT_RECOMMENDED.value
    ]
    if not positive:
        issues.append("no binding positive editorial review")

    # 5. Every change must be auditable.
    if not payload.audit_log_present:
        issues.append("audit log entry missing")

    return GateResult(allowed=not issues, issues=tuple(issues))
