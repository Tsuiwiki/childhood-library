"""MediaAsset / StorageLocation / PlaybackResource (DATABASE_DESIGN.md 3.7-3.9).

MEDIA_ASSET_DESIGN.md: asset_id is decoupled from provider URLs; a container
only ever holds `local` at this stage. A published asset requires a checksum
AND verified rights. Official preview URLs are never persisted.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import (
    AccessMethod,
    AssetRole,
    MediaType,
    PublicationStatus,
    ResourceType,
    ReviewStatus,
    RightsStatus,
    StorageProvider,
    in_check,
)


class MediaAsset(TimestampMixin, Base):
    __tablename__ = "media_assets"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("works.work_id", ondelete="SET NULL")
    )
    work_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_versions.work_version_id", ondelete="SET NULL")
    )
    # Polymorphic back-references are plain UUIDs (no FK) to keep the
    # media_assets <-> recording_versions dependency acyclic. The application
    # layer validates existence and asset_role.
    recording_version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    score_edition_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    derived_from_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_assets.asset_id", ondelete="SET NULL")
    )
    rights_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rights_records.rights_record_id", ondelete="SET NULL")
    )
    asset_role: Mapped[str] = mapped_column(String(32), nullable=False)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(150))
    file_extension: Mapped[str | None] = mapped_column(String(20))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    rights_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=RightsStatus.UNKNOWN.value
    )
    publication_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=PublicationStatus.DRAFT.value
    )
    storage_note: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        CheckConstraint(in_check("asset_role", AssetRole), name="asset_role"),
        CheckConstraint(in_check("media_type", MediaType), name="media_type"),
        CheckConstraint(in_check("rights_status", RightsStatus), name="rights_status"),
        CheckConstraint(
            in_check("publication_status", PublicationStatus),
            name="publication_status",
        ),
        CheckConstraint(
            "publication_status <> 'published' OR "
            "(checksum_sha256 IS NOT NULL AND rights_status = 'verified')",
            name="published_requires_checksum_and_verified_rights",
        ),
        # Duplicate DETECTION, not hard rejection: a human must confirm.
        Index("ix_media_assets_checksum", "checksum_sha256", "file_size_bytes"),
    )


class StorageLocation(TimestampMixin, Base):
    __tablename__ = "storage_locations"

    storage_location_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("media_assets.asset_id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(
        String(32), nullable=False, default=StorageProvider.LOCAL.value
    )
    region: Mapped[str | None] = mapped_column(String(120))
    bucket: Mapped[str | None] = mapped_column(String(200))
    object_key: Mapped[str | None] = mapped_column(String(1000))
    storage_class: Mapped[str | None] = mapped_column(String(80))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    replica_status: Mapped[str | None] = mapped_column(String(32))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    byte_size: Mapped[int | None] = mapped_column(BigInteger)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))

    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "provider",
            "object_key",
            name="storage_location_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("provider", StorageProvider), name="provider"),
        CheckConstraint(
            "provider <> 'local' OR object_key IS NOT NULL",
            name="local_requires_object_key",
        ),
        Index(
            "uq_storage_locations_one_primary",
            "asset_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )


class PlaybackResource(TimestampMixin, Base):
    __tablename__ = "playback_resources"

    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_assets.asset_id", ondelete="CASCADE")
    )
    recording_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recording_versions.recording_version_id", ondelete="CASCADE")
    )
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(120))
    provider_resource_id: Mapped[str | None] = mapped_column(String(300))
    external_url: Mapped[str | None] = mapped_column(Text)
    access_policy: Mapped[str] = mapped_column(
        String(24), nullable=False, default=AccessMethod.NONE.value
    )
    review_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=ReviewStatus.PENDING.value
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    embed_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    embed_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rights_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rights_records.rights_record_id", ondelete="SET NULL")
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_resource_id",
            "resource_type",
            name="playback_resource_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("resource_type", ResourceType), name="resource_type"),
        CheckConstraint(in_check("access_policy", AccessMethod), name="access_policy"),
        CheckConstraint(in_check("review_status", ReviewStatus), name="review_status"),
        CheckConstraint(
            "embed_enabled = false OR embed_allowed = true",
            name="embed_requires_permission",
        ),
        CheckConstraint(
            "resource_type <> 'official_preview' OR external_url IS NULL",
            name="official_preview_url_not_persisted",
        ),
        CheckConstraint(
            "asset_id IS NOT NULL OR recording_version_id IS NOT NULL",
            name="playback_has_owner",
        ),
    )
