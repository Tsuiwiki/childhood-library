"""Media access decisions (MEDIA_ASSET_DESIGN.md section 8, PROJECT_PRINCIPLES).

Three levels are deliberately separate:

* ``research_metadata`` - ALWAYS allowed. Rights unknown must never block
  internal research cataloguing (PROJECT_PRINCIPLES.md).
* ``internal_content``  - bytes may be read inside the trusted, loopback-only
  environment. Requires a recorded checksum that still verifies.
* ``public_url``        - a public playback address may be issued. Requires a
  live verified clearance, publication, approved playback and a real access
  method.

This module DECIDES. It never creates, stores or returns a URL; temporary
signed addresses are issued by a later caller only after ``public_url`` is True.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.publication_gate import rights_clearance_is_valid
from app.domain.status import PublicationStatus, RightsStatus
from app.models.enums import AccessMethod, ReviewStatus


class MediaAccessDenied(Exception):
    """Raised when a caller tries to serve bytes without a granted decision."""


@dataclass(frozen=True)
class MediaAccessInput:
    checksum_sha256: str | None = None
    integrity_ok: bool = True
    rights_status: str = RightsStatus.UNKNOWN.value
    publication_status: str = PublicationStatus.DRAFT.value
    review_status: str = ReviewStatus.PENDING.value
    access_policy: str = AccessMethod.NONE.value
    rights_valid_until: date | None = None
    embed_enabled: bool = False
    embed_allowed: bool = False
    today: date | None = None


@dataclass(frozen=True)
class MediaAccessDecision:
    research_metadata: bool
    internal_content: bool
    public_url: bool
    issues: tuple[str, ...]
    internal_issues: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "research_metadata": self.research_metadata,
            "internal_content": self.internal_content,
            "public_url": self.public_url,
            "issues": list(self.issues),
            "internal_issues": list(self.internal_issues),
        }


def evaluate_media_access(payload: MediaAccessInput) -> MediaAccessDecision:
    internal_issues: list[str] = []
    public_issues: list[str] = []

    # 1. Internal content requires integrity, never a rights clearance.
    if not payload.checksum_sha256:
        internal_issues.append("checksum_sha256 is missing")
    if not payload.integrity_ok:
        internal_issues.append("integrity check failed")
    if payload.rights_status == RightsStatus.REVOKED.value:
        internal_issues.append("rights revoked")
    if payload.publication_status == PublicationStatus.WITHDRAWN.value:
        internal_issues.append("asset withdrawn")
    internal_content = not internal_issues

    # 2. Public URL issuance builds on top of internal_content.
    if not internal_content:
        public_issues.extend("internal content blocked: %s" % i for i in internal_issues)
    if not rights_clearance_is_valid(
        payload.rights_status, payload.rights_valid_until, payload.today
    ):
        public_issues.append("no live verified rights clearance")
    if payload.publication_status != PublicationStatus.PUBLISHED.value:
        public_issues.append("publication_status is not 'published'")
    if payload.review_status != ReviewStatus.APPROVED.value:
        public_issues.append("playback resource is not approved")
    if payload.access_policy == AccessMethod.NONE.value:
        public_issues.append("access_policy is 'none'")
    if payload.embed_enabled and not payload.embed_allowed:
        public_issues.append("embed enabled without permission")

    return MediaAccessDecision(
        research_metadata=True,
        internal_content=internal_content,
        public_url=not public_issues,
        issues=tuple(public_issues),
        internal_issues=tuple(internal_issues),
    )


def require_internal_content(decision: MediaAccessDecision) -> None:
    if not decision.internal_content:
        raise MediaAccessDenied("; ".join(decision.internal_issues) or "access denied")


def require_public_url(decision: MediaAccessDecision) -> None:
    if not decision.public_url:
        raise MediaAccessDenied("; ".join(decision.issues) or "public URL denied")
