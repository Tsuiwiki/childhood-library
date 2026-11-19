"""Person and Contribution (DATABASE_DESIGN.md 3.2).

Unknown authors stay NULL and are explicitly flagged `is_unknown_author`;
the schema never invents a name. One person may hold several roles on one work.
"""
from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import Confidence, ContributionRole, in_check


class Person(TimestampMixin, Base):
    __tablename__ = "people"

    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(300), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    life_years: Mapped[str | None] = mapped_column(String(80))
    region: Mapped[str | None] = mapped_column(String(120))
    disambiguation_note: Mapped[str | None] = mapped_column(Text)


class Contribution(TimestampMixin, Base):
    __tablename__ = "contributions"

    contribution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("people.person_id", ondelete="RESTRICT")
    )
    work_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_versions.work_version_id", ondelete="SET NULL")
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    credited_as: Mapped[str | None] = mapped_column(String(300))
    confidence: Mapped[str] = mapped_column(
        String(16), nullable=False, default=Confidence.LOW.value
    )
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_records.source_record_id", ondelete="SET NULL")
    )
    is_unknown_author: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    role_note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "work_id",
            "person_id",
            "role",
            "work_version_id",
            name="contribution_business_key",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(in_check("role", ContributionRole), name="role"),
        CheckConstraint(in_check("confidence", Confidence), name="confidence"),
        CheckConstraint(
            "is_unknown_author = false OR person_id IS NULL",
            name="unknown_author_has_no_person",
        ),
    )
