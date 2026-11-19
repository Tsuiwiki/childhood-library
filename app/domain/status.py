"""Five independent status dimensions.

Source: PROJECT_PRINCIPLES.md L83-L87, DATA_MODEL.md L76-L81,
DATABASE_DESIGN.md L157-L161. These enums stay pure Python: T-06 landed them as
five independent columns + CHECK constraints on `works`, with per-object
clearance in `rights_records`. Keeping them as separate types prevents later
code from collapsing "研究完成 / 权利确认 / 质量适合 / 访问方式 / 公开发布" into
one review flag.
"""
from enum import StrEnum


class ResearchStatus(StrEnum):
    DISCOVERED = "discovered"
    RESEARCHING = "researching"
    REVIEWED = "reviewed"
    REJECTED = "rejected"


class RightsStatus(StrEnum):
    UNKNOWN = "unknown"
    PENDING = "pending"
    VERIFIED = "verified"
    RESTRICTED = "restricted"
    REVOKED = "revoked"


class QualityStatus(StrEnum):
    UNREVIEWED = "unreviewed"
    SUITABLE = "suitable"
    NEEDS_CONTEXT = "needs_context"
    UNSUITABLE = "unsuitable"


class AccessMethod(StrEnum):
    NONE = "none"
    SOURCE_LINK = "source_link"
    OFFICIAL_EMBED = "official_embed"
    LICENSED_MEDIA = "licensed_media"
    OWN_ORIGINAL = "own_original"


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


STATUS_DIMENSIONS = {
    "research_status": ResearchStatus,
    "rights_status": RightsStatus,
    "quality_status": QualityStatus,
    "access_method": AccessMethod,
    "publication_status": PublicationStatus,
}
