"""SourceRecord: evidence for one fact about one entity.

DATABASE_DESIGN.md 3.6. Polymorphic association by design (no cross-table FK);
existence of the referenced entity is checked in the application layer.
A URL is evidence, never a rights clearance.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import (
    Confidence,
    EvidenceScope,
    SourceType,
    VerificationStatus,
    in_check,
)


class SourceRecord(TimestampMixin, Base):
    __tablename__ = "source_records"

    source_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    supports_entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    supports_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=SourceType.OTHER.value
    )
    platform: Mapped[str | None] = mapped_column(String(200))
    publisher: Mapped[str | None] = mapped_column(String(300))
    source_title: Mapped[str | None] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[str | None] = mapped_column(String(40))
    accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence_scope: Mapped[str] = mapped_column(
        String(32), nullable=False, default=EvidenceScope.IDENTITY.value
    )
    evidence_note: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(
        String(16), nullable=False, default=Confidence.LOW.value
    )
    verification_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=VerificationStatus.UNCHECKED.value
    )
    checked_by: Mapped[str | None] = mapped_column(String(120))
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String(128))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "source_url",
            "supports_entity_type",
            "supports_entity_id",
            "evidence_scope",
            name="source_evidence_unique",
        ),
        CheckConstraint(in_check("source_type", SourceType), name="source_type"),
        CheckConstraint(
            in_check("evidence_scope", EvidenceScope), name="evidence_scope"
        ),
        CheckConstraint(in_check("confidence", Confidence), name="confidence"),
        CheckConstraint(
            in_check("verification_status", VerificationStatus),
            name="verification_status",
        ),
        CheckConstraint(
            "verification_status <> 'checked' OR (checked_by IS NOT NULL AND checked_at IS NOT NULL)",
            name="checked_requires_auditor",
        ),
        Index(
            "ix_source_records_supports",
            "supports_entity_type",
            "supports_entity_id",
        ),
    )
