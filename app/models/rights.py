"""RightsRecord: per-object licence and clearance (DATABASE_DESIGN.md 3.10).

`subject_type` + `subject_id` is polymorphic; one object may hold several
records for different territories / uses. Source evidence and rights clearance
are deliberately separate entities.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import RightsStatus, RightsSubjectType, in_check


class RightsRecord(TimestampMixin, Base):
    __tablename__ = "rights_records"

    rights_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    rights_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=RightsStatus.UNKNOWN.value
    )
    rights_holder: Mapped[str | None] = mapped_column(String(300))
    license_name: Mapped[str | None] = mapped_column(String(300))
    license_url: Mapped[str | None] = mapped_column(Text)
    territory: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    permitted_uses: Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    attribution_requirement: Mapped[str | None] = mapped_column(Text)
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    evidence_url: Mapped[str | None] = mapped_column(Text)
    evidence_note: Mapped[str | None] = mapped_column(Text)
    reviewer: Mapped[str | None] = mapped_column(String(120))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_records.source_record_id", ondelete="SET NULL")
    )

    __table_args__ = (
        CheckConstraint(
            in_check("subject_type", RightsSubjectType), name="subject_type"
        ),
        CheckConstraint(in_check("rights_status", RightsStatus), name="rights_status"),
        CheckConstraint(
            "valid_from IS NULL OR valid_until IS NULL OR valid_until >= valid_from",
            name="validity_range",
        ),
        CheckConstraint(
            "rights_status <> 'verified' OR (reviewer IS NOT NULL AND reviewed_at IS NOT NULL)",
            name="verified_requires_reviewer",
        ),
        Index("ix_rights_records_subject", "subject_type", "subject_id"),
    )
