"""T-06 ORM model registry.

Importing this package registers every table on ``Base.metadata``; Alembic's
env.py uses it as ``target_metadata``. No data is inserted here.
"""
from app.models.base import Base, NAMING_CONVENTION
from app.models.contribution import Contribution, Person
from app.models.media import MediaAsset, PlaybackResource, StorageLocation
from app.models.review import REVIEW_SCORE_DIMENSIONS, EditorialReview
from app.models.rights import RightsRecord
from app.models.source import SourceRecord
from app.models.support import (
    AuditLog,
    Collection,
    CollectionMembership,
    ExternalIdentifier,
    ImportBatch,
    Tag,
    WorkRelation,
    WorkTag,
)
from app.models.version import RecordingVersion, ScoreEdition, WorkVersion
from app.models.work import Work

target_metadata = Base.metadata

CORE_ENTITIES = (
    "works",
    "contributions",
    "work_versions",
    "recording_versions",
    "score_editions",
    "source_records",
    "media_assets",
    "playback_resources",
    "rights_records",
    "editorial_reviews",
)

SUPPORT_TABLES = (
    "people",
    "storage_locations",
    "external_identifiers",
    "collections",
    "collection_memberships",
    "tags",
    "work_tags",
    "work_relations",
    "import_batches",
    "audit_logs",
)

ALL_TABLES = CORE_ENTITIES + SUPPORT_TABLES

__all__ = [
    "ALL_TABLES",
    "CORE_ENTITIES",
    "NAMING_CONVENTION",
    "REVIEW_SCORE_DIMENSIONS",
    "SUPPORT_TABLES",
    "Base",
    "target_metadata",
    "Work",
    "Person",
    "Contribution",
    "WorkVersion",
    "RecordingVersion",
    "ScoreEdition",
    "SourceRecord",
    "MediaAsset",
    "StorageLocation",
    "PlaybackResource",
    "RightsRecord",
    "EditorialReview",
    "ExternalIdentifier",
    "Collection",
    "CollectionMembership",
    "Tag",
    "WorkTag",
    "WorkRelation",
    "ImportBatch",
    "AuditLog",
]
