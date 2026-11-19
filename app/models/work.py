"""Work: the abstract work, shared by all three libraries.

DATABASE_DESIGN.md 3.1 / DATA_MODEL.md 11. Music-only fields live in the
`metadata` JSONB column so story and poem works do not inherit empty columns.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import (
    AccessMethod,
    CatalogStatus,
    Pillar,
    PublicationStatus,
    QualityStatus,
    ResearchStatus,
    RightsStatus,
    WorkType,
    in_check,
)


class Work(TimestampMixin, Base):
    __tablename__ = "works"

    work_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    canonical_title: Mapped[str] = mapped_column(String(500), nullable=False)
    work_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=WorkType.UNKNOWN.value
    )
    pillar: Mapped[str] = mapped_column(
        String(32), nullable=False, default=Pillar.PENDING.value
    )
    language: Mapped[str | None] = mapped_column(String(35))
    region: Mapped[str | None] = mapped_column(String(120))
    culture: Mapped[str | None] = mapped_column(String(120))
    era_start_year: Mapped[int | None] = mapped_column(Integer)
    era_end_year: Mapped[int | None] = mapped_column(Integer)
    first_published_at: Mapped[str | None] = mapped_column(String(40))
    summary: Mapped[str | None] = mapped_column(Text)
    historical_context: Mapped[str | None] = mapped_column(Text)
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    # Five independent dimensions. `rights_status` here is the work-level
    # copyright dimension only; per-object licences live in rights_records.
    research_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=ResearchStatus.DISCOVERED.value
    )
    rights_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=RightsStatus.UNKNOWN.value
    )
    quality_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=QualityStatus.UNREVIEWED.value
    )
    access_method: Mapped[str] = mapped_column(
        String(24), nullable=False, default=AccessMethod.NONE.value
    )
    publication_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=PublicationStatus.DRAFT.value
    )
    catalog_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CatalogStatus.BIBLIOGRAPHY_CANDIDATE.value
    )

    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("import_batches.import_batch_id", ondelete="SET NULL")
    )

    __table_args__ = (
        CheckConstraint(in_check("work_type", WorkType), name="work_type"),
        CheckConstraint(in_check("pillar", Pillar), name="pillar"),
        CheckConstraint(in_check("catalog_status", CatalogStatus), name="catalog_status"),
        CheckConstraint(in_check("research_status", ResearchStatus), name="research_status"),
        CheckConstraint(in_check("rights_status", RightsStatus), name="rights_status"),
        CheckConstraint(in_check("quality_status", QualityStatus), name="quality_status"),
        CheckConstraint(in_check("access_method", AccessMethod), name="access_method"),
        CheckConstraint(
            in_check("publication_status", PublicationStatus), name="publication_status"
        ),
        CheckConstraint(
            "era_start_year IS NULL OR era_end_year IS NULL OR era_start_year <= era_end_year",
            name="era_range",
        ),
        # Single-table part of the publication gate (DATABASE_DESIGN.md 4.1).
        CheckConstraint(
            "publication_status <> 'published' OR quality_status = 'suitable'",
            name="published_requires_suitable",
        ),
        Index("ix_works_canonical_title", "canonical_title"),
        # De-duplication hint ONLY: same-title variants are legitimate.
        Index(
            "ix_works_dedup_hint",
            "canonical_title",
            "work_type",
            "language",
            "region",
        ),
    )
