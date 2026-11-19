"""Supporting tables (DATABASE_DESIGN.md 3.11).

ExternalIdentifier is what makes the three legacy ID families mappable onto a
stable work_id. ImportBatch / AuditLog give every later import a rollback unit
and a full trail for rights, publication and review changes.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.enums import ImportBatchStatus, RelationType, in_check


class ExternalIdentifier(TimestampMixin, Base):
    __tablename__ = "external_identifiers"

    external_identifier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    # namespace separates the three colliding legacy ID families, e.g.
    # century_vol1 / century_vol4 / catalog_candidate / prototype_cn.
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    identifier: Mapped[str] = mapped_column(String(120), nullable=False)
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("namespace", "identifier", name="external_identifier_unique"),
        Index("ix_external_identifiers_work", "work_id"),
    )


class Collection(TimestampMixin, Base):
    __tablename__ = "collections"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, default="topic")
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )


class CollectionMembership(TimestampMixin, Base):
    __tablename__ = "collection_memberships"

    membership_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("collections.collection_id", ondelete="CASCADE"), nullable=False
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "collection_id", "work_id", name="collection_membership_unique"
        ),
    )


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    tag_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    namespace: Mapped[str] = mapped_column(
        String(64), nullable=False, default="default"
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    __table_args__ = (UniqueConstraint("namespace", "name", name="tag_unique"),)


class WorkTag(TimestampMixin, Base):
    __tablename__ = "work_tags"

    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True
    )


class WorkRelation(TimestampMixin, Base):
    __tablename__ = "work_relations"

    relation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    related_work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "work_id", "related_work_id", "relation_type", name="work_relation_unique"
        ),
        CheckConstraint(in_check("relation_type", RelationType), name="relation_type"),
        CheckConstraint("work_id <> related_work_id", name="no_self_relation"),
    )


class ImportBatch(TimestampMixin, Base):
    __tablename__ = "import_batches"

    import_batch_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default=ImportBatchStatus.RUNNING.value
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    counts: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(in_check("status", ImportBatchStatus), name="status"),
    )


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("import_batches.import_batch_id", ondelete="SET NULL")
    )

    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_occurred_at", "occurred_at"),
    )
