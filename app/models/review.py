"""EditorialReview: aesthetic judgement bound to a concrete recording version.

DATABASE_DESIGN.md 3.10 and MUSIC_LIBRARY_MASTER_PLAN.md 3. Seven score
dimensions are kept in JSONB so different libraries can use different rubrics
without altering the shared table. AI output is advisory and never binding.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import ReviewConclusion, RightsSubjectType, in_check

REVIEW_SCORE_DIMENSIONS = (
    "melody_beauty",
    "childlike_expression",
    "lyric_literary_quality",
    "music_quality",
    "cultural_value",
    "replay_value",
    "age_appropriateness",
)


class EditorialReview(TimestampMixin, Base):
    __tablename__ = "editorial_reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    reviewed_recording_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recording_versions.recording_version_id", ondelete="SET NULL")
    )
    scores: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    conclusion: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(120), nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(Text)
    is_ai_suggestion: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_binding: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint(
            in_check("subject_type", RightsSubjectType), name="subject_type"
        ),
        CheckConstraint(in_check("conclusion", ReviewConclusion), name="conclusion"),
        CheckConstraint(
            "is_ai_suggestion = false OR is_binding = false",
            name="ai_suggestion_is_not_binding",
        ),
        Index("ix_editorial_reviews_subject", "subject_type", "subject_id"),
    )
