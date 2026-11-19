"""Database-level value sets for the T-06 schema.

Strategy (DATABASE_DESIGN.md section 8 decision): VARCHAR + CHECK instead of
PostgreSQL native ENUM. The five status dimensions are imported from
app/domain/status.py so the T-05 contract and the T-06 columns cannot drift.
"""
from __future__ import annotations

from enum import StrEnum

from app.domain.status import (
    AccessMethod,
    PublicationStatus,
    QualityStatus,
    ResearchStatus,
    RightsStatus,
)


def enum_values(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(member.value for member in enum_cls)


def in_check(column: str, enum_cls: type[StrEnum]) -> str:
    """Build a CHECK expression, e.g. ``research_status IN ('discovered', ...)``."""
    return "%s IN (%s)" % (
        column,
        ", ".join("'%s'" % value for value in enum_values(enum_cls)),
    )


class WorkType(StrEnum):
    SONG = "song"
    NURSERY_RHYME = "nursery_rhyme"
    FOLK_SONG = "folk_song"
    INSTRUMENTAL = "instrumental"
    ORIGINAL = "original"
    UNKNOWN = "unknown"


class Pillar(StrEnum):
    CHINESE_CLASSIC = "chinese_classic"
    WORLD_CLASSIC = "world_classic"
    ORIGINAL = "original"
    PENDING = "pending"


class CatalogStatus(StrEnum):
    BIBLIOGRAPHY_CANDIDATE = "bibliography_candidate"
    METADATA_VERIFIED = "metadata_verified"
    CORE_SELECTED = "core_selected"
    NOT_SELECTED = "not_selected"


class LyricsStatus(StrEnum):
    VERIFIED = "verified"
    NO_LYRIC_APPLICABLE = "no_lyric_applicable"
    PENDING = "pending"


class VersionType(StrEnum):
    ORIGINAL = "original"
    TRANSLATION = "translation"
    ADAPTATION = "adaptation"
    REGIONAL = "regional"
    EDITORIAL = "editorial"


class ContributionRole(StrEnum):
    LYRICIST = "lyricist"
    COMPOSER = "composer"
    TRANSLATOR = "translator"
    ADAPTER = "adapter"
    ARRANGER = "arranger"
    COLLECTOR = "collector"
    EDITOR = "editor"
    PERFORMER = "performer"
    CONDUCTOR = "conductor"
    ENSEMBLE = "ensemble"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScoreType(StrEnum):
    NUMBERED = "numbered"
    STAFF = "staff"
    PIANO = "piano"
    CHORAL = "choral"
    MUSICXML = "musicxml"
    OTHER = "other"


class SourceType(StrEnum):
    BOOK = "book"
    JOURNAL = "journal"
    ARCHIVE = "archive"
    LIBRARY_CATALOG = "library_catalog"
    OFFICIAL_SITE = "official_site"
    WEB_PAGE = "web_page"
    AUDIO_LINER = "audio_liner"
    OTHER = "other"


class EvidenceScope(StrEnum):
    IDENTITY = "identity"
    AUTHOR = "author"
    DATING = "dating"
    VERSION = "version"
    RECORDING = "recording"
    SCORE = "score"
    RIGHTS = "rights"


class VerificationStatus(StrEnum):
    UNCHECKED = "unchecked"
    CHECKED = "checked"
    DISPUTED = "disputed"


class AssetRole(StrEnum):
    RECORDING = "recording"
    SCORE = "score"
    COVER = "cover"
    LYRIC_SHEET = "lyric_sheet"
    REFERENCE = "reference"
    DERIVED_RENDER = "derived_render"


class MediaType(StrEnum):
    AUDIO = "audio"
    IMAGE = "image"
    SCORE_XML = "score_xml"
    DOCUMENT = "document"
    VIDEO = "video"
    OTHER = "other"


class StorageProvider(StrEnum):
    LOCAL = "local"
    TENCENT_COS = "tencent_cos"
    BAIDU_BOS = "baidu_bos"
    S3_COMPATIBLE = "s3_compatible"


class ResourceType(StrEnum):
    EXTERNAL_LINK = "external_link"
    OFFICIAL_PREVIEW = "official_preview"
    HOSTED_ASSET = "hosted_asset"
    OFFICIAL_EMBED = "official_embed"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RightsSubjectType(StrEnum):
    WORK = "work"
    WORK_VERSION = "work_version"
    RECORDING_VERSION = "recording_version"
    SCORE_EDITION = "score_edition"
    MEDIA_ASSET = "media_asset"


class ReviewConclusion(StrEnum):
    CORE = "core"
    CULTURAL = "cultural"
    EXTENDED = "extended"
    HISTORICAL_REFERENCE = "historical_reference"
    NOT_RECOMMENDED = "not_recommended"


class RecordingKind(StrEnum):
    HISTORICAL_FIRST = "historical_first"
    FIELD_RECORDING = "field_recording"
    CHILDREN_CHORUS = "children_chorus"
    MODERN_COVER = "modern_cover"
    INSTRUMENTAL = "instrumental"
    ANIMATION = "animation"
    OTHER = "other"


class RelationType(StrEnum):
    VARIANT_OF = "variant_of"
    ADAPTED_FROM = "adapted_from"
    INCLUDED_IN = "included_in"
    RELATED_TO = "related_to"


class ImportBatchStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# Five independent dimensions: never collapse them into one review flag.
STATUS_DIMENSION_COLUMNS = {
    "research_status": ResearchStatus,
    "rights_status": RightsStatus,
    "quality_status": QualityStatus,
    "access_method": AccessMethod,
    "publication_status": PublicationStatus,
}

# Every enum that gets a CHECK constraint; consumed by tests and Alembic.
DB_ENUMS = (
    WorkType,
    Pillar,
    CatalogStatus,
    LyricsStatus,
    VersionType,
    ContributionRole,
    Confidence,
    ScoreType,
    SourceType,
    EvidenceScope,
    VerificationStatus,
    AssetRole,
    MediaType,
    StorageProvider,
    ResourceType,
    ReviewStatus,
    RightsSubjectType,
    ReviewConclusion,
    RecordingKind,
    RelationType,
    ImportBatchStatus,
    ResearchStatus,
    RightsStatus,
    QualityStatus,
    AccessMethod,
    PublicationStatus,
)

# Kept free of SQLAlchemy imports so the pure-Python publication gate and the
# local (no-SQLAlchemy) test run can import these enums safely.
__all__ = ["DB_ENUMS", "STATUS_DIMENSION_COLUMNS", "enum_values", "in_check"]
