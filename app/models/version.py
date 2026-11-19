"""WorkVersion / RecordingVersion / ScoreEdition (DATABASE_DESIGN.md 3.3-3.5).

A work may carry many regional / dialect / translated text versions, many
recordings and many score editions. `no_lyric_applicable` is a resolved verdict,
NOT a pending placeholder, and must never be back-filled with guessed lyrics.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import (
    LyricsStatus,
    RecordingKind,
    ScoreType,
    VersionType,
    in_check,
)


class WorkVersion(TimestampMixin, Base):
    __tablename__ = "work_versions"

    work_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_versions.work_version_id", ondelete="SET NULL")
    )
    version_label: Mapped[str] = mapped_column(String(200), nullable=False)
    version_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=VersionType.ORIGINAL.value
    )
    language: Mapped[str | None] = mapped_column(String(35))
    region: Mapped[str | None] = mapped_column(String(120))
    lyrics_text: Mapped[str | None] = mapped_column(Text)
    lyrics_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=LyricsStatus.PENDING.value
    )
    lyrics_source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_records.source_record_id", ondelete="SET NULL")
    )
    verdict_note: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "work_id",
            "version_label",
            "language",
            name="work_version_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("version_type", VersionType), name="version_type"),
        CheckConstraint(in_check("lyrics_status", LyricsStatus), name="lyrics_status"),
        CheckConstraint(
            "lyrics_status <> 'no_lyric_applicable' OR verdict_note IS NOT NULL",
            name="verdict_requires_note",
        ),
        CheckConstraint(
            "lyrics_status <> 'no_lyric_applicable' OR lyrics_text IS NULL",
            name="no_lyric_applicable_has_no_text",
        ),
        CheckConstraint(
            "lyrics_text IS NULL OR lyrics_source_id IS NOT NULL",
            name="lyrics_requires_source",
        ),
    )


class RecordingVersion(TimestampMixin, Base):
    __tablename__ = "recording_versions"

    recording_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    work_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_versions.work_version_id", ondelete="SET NULL")
    )
    performer_text: Mapped[str | None] = mapped_column(String(500))
    ensemble_text: Mapped[str | None] = mapped_column(String(500))
    recording_year: Mapped[int | None] = mapped_column(Integer)
    release_year: Mapped[int | None] = mapped_column(Integer)
    album_title: Mapped[str | None] = mapped_column(String(500))
    label: Mapped[str | None] = mapped_column(String(300))
    catalog_number: Mapped[str | None] = mapped_column(String(120))
    arranger_text: Mapped[str | None] = mapped_column(String(300))
    instrumentation: Mapped[str | None] = mapped_column(String(300))
    performance_form: Mapped[str | None] = mapped_column(String(120))
    version_label: Mapped[str | None] = mapped_column(String(200))
    version_kind: Mapped[str] = mapped_column(
        String(32), nullable=False, default=RecordingKind.OTHER.value
    )
    version_note: Mapped[str | None] = mapped_column(Text)
    is_historical_first: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_records.source_record_id", ondelete="SET NULL")
    )
    primary_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_assets.asset_id", ondelete="SET NULL")
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "work_id",
            "performer_text",
            "recording_year",
            "label",
            "version_label",
            name="recording_version_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("version_kind", RecordingKind), name="version_kind"),
        CheckConstraint(
            "recording_year IS NULL OR recording_year BETWEEN 1800 AND 2100",
            name="recording_year_range",
        ),
        CheckConstraint(
            "is_historical_first = false OR version_kind IN ('historical_first', 'field_recording')",
            name="modern_cover_is_not_historical_first",
        ),
    )


class ScoreEdition(TimestampMixin, Base):
    __tablename__ = "score_editions"

    score_edition_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    work_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_versions.work_version_id", ondelete="SET NULL")
    )
    score_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ScoreType.OTHER.value
    )
    key_signature: Mapped[str | None] = mapped_column(String(40))
    time_signature: Mapped[str | None] = mapped_column(String(40))
    voices: Mapped[str | None] = mapped_column(String(200))
    completeness: Mapped[str | None] = mapped_column(String(80))
    publisher: Mapped[str | None] = mapped_column(String(300))
    book_title: Mapped[str | None] = mapped_column(String(500))
    edition: Mapped[str | None] = mapped_column(String(120))
    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)
    isbn: Mapped[str | None] = mapped_column(String(40))
    arranger_text: Mapped[str | None] = mapped_column(String(300))
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_records.source_record_id", ondelete="SET NULL")
    )
    rights_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rights_records.rights_record_id", ondelete="SET NULL")
    )
    primary_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_assets.asset_id", ondelete="SET NULL")
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "work_id",
            "publisher",
            "book_title",
            "edition",
            "page_start",
            "score_type",
            name="score_edition_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("score_type", ScoreType), name="score_type"),
        CheckConstraint(
            "page_start IS NULL OR page_end IS NULL OR page_start <= page_end",
            name="page_range",
        ),
    )
