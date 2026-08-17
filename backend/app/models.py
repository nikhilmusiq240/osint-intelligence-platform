from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    targets: Mapped[list[InvestigationTarget]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[InvestigationJob]] = relationship(back_populates="investigation")
    entities: Mapped[list[EntityRecord]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan"
    )
    evidence_items: Mapped[list[EvidenceRecord]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan"
    )
    relationships: Mapped[list[RelationshipRecord]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan"
    )
    connector_runs: Mapped[list[ConnectorRun]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan"
    )


class InvestigationTarget(Base):
    __tablename__ = "investigation_targets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    investigation: Mapped[Investigation] = relationship(back_populates="targets")
    entities: Mapped[list[EntityRecord]] = relationship(back_populates="target")
    evidence_items: Mapped[list[EvidenceRecord]] = relationship(back_populates="target")
    connector_runs: Mapped[list[ConnectorRun]] = relationship(back_populates="target")


class InvestigationJob(Base):
    __tablename__ = "investigation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    connector_name: Mapped[str] = mapped_column(String(100), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    investigation: Mapped[Investigation] = relationship(back_populates="jobs")


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), default="manual", nullable=False
    )
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    provenance_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    def __init__(
        self,
        *,
        source_name: str,
        source_type: str = "manual",
        source_url: str | None = None,
        retrieved_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.source_name = source_name
        self.source_type = source_type
        self.source_url = source_url
        self.retrieved_at = retrieved_at
        self.provenance_metadata = metadata

    evidence_items: Mapped[list[EvidenceRecord]] = relationship(
        back_populates="provenance_record"
    )
    entities: Mapped[list[EntityRecord]] = relationship(back_populates="provenance")
    relationships: Mapped[list[RelationshipRecord]] = relationship(
        back_populates="provenance"
    )


class EntityRecord(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    target_id: Mapped[int | None] = mapped_column(
        ForeignKey("investigation_targets.id"), nullable=True
    )
    provenance_id: Mapped[int | None] = mapped_column(
        ForeignKey("provenance_records.id"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    is_observed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    investigation: Mapped[Investigation] = relationship(back_populates="entities")
    target: Mapped[InvestigationTarget | None] = relationship(back_populates="entities")
    provenance: Mapped[ProvenanceRecord | None] = relationship(
        back_populates="entities"
    )
    source_evidence: Mapped[list[EvidenceRecord]] = relationship(
        back_populates="entity"
    )
    outgoing_relationships: Mapped[list[RelationshipRecord]] = relationship(
        back_populates="source_entity",
        foreign_keys="RelationshipRecord.source_entity_id",
    )
    incoming_relationships: Mapped[list[RelationshipRecord]] = relationship(
        back_populates="target_entity",
        foreign_keys="RelationshipRecord.target_entity_id",
    )


class RelationshipRecord(Base):
    __tablename__ = "entity_relationships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    source_entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"), nullable=False
    )
    target_entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"), nullable=False
    )
    provenance_id: Mapped[int | None] = mapped_column(
        ForeignKey("provenance_records.id"), nullable=True
    )
    relation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    investigation: Mapped[Investigation] = relationship(back_populates="relationships")
    provenance: Mapped[ProvenanceRecord | None] = relationship(
        back_populates="relationships"
    )
    source_entity: Mapped[EntityRecord] = relationship(
        back_populates="outgoing_relationships", foreign_keys=[source_entity_id]
    )
    target_entity: Mapped[EntityRecord] = relationship(
        back_populates="incoming_relationships", foreign_keys=[target_entity_id]
    )


class EvidenceRecord(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    target_id: Mapped[int | None] = mapped_column(
        ForeignKey("investigation_targets.id"), nullable=True
    )
    entity_id: Mapped[int | None] = mapped_column(
        ForeignKey("entities.id"), nullable=True
    )
    provenance_id: Mapped[int | None] = mapped_column(
        ForeignKey("provenance_records.id"), nullable=True
    )
    provenance_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(
        String(50), default="text", nullable=False
    )
    hash_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    observed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retrieved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    connector_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    connector_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_source_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __init__(
        self,
        *,
        provenance: dict[str, Any] | None = None,
        raw_source_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if provenance is not None:
            self.provenance_metadata = provenance
        if raw_source_data is not None:
            self.raw_source_data = raw_source_data

    @property
    def provenance(self) -> dict[str, Any] | None:
        if self.provenance_record is not None:
            return self.provenance_record.provenance_metadata or {}
        return self.provenance_metadata or {}

    @provenance.setter
    def provenance(self, value: dict[str, Any] | None) -> None:
        self.provenance_metadata = value

    investigation: Mapped[Investigation] = relationship(back_populates="evidence_items")
    target: Mapped[InvestigationTarget | None] = relationship(
        back_populates="evidence_items"
    )
    entity: Mapped[EntityRecord | None] = relationship(back_populates="source_evidence")
    provenance_record: Mapped[ProvenanceRecord | None] = relationship(
        back_populates="evidence_items"
    )


class ConnectorRun(Base):
    __tablename__ = "connector_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"), nullable=False
    )
    target_id: Mapped[int | None] = mapped_column(
        ForeignKey("investigation_targets.id"), nullable=True
    )
    connector_name: Mapped[str] = mapped_column(String(100), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    run_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __init__(
        self, *, metadata: dict[str, Any] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if metadata is not None:
            self.run_metadata = metadata

    investigation: Mapped[Investigation] = relationship(back_populates="connector_runs")
    target: Mapped[InvestigationTarget | None] = relationship(
        back_populates="connector_runs"
    )


class ConnectorModel(Base):
    __tablename__ = "connectors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
