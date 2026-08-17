from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ConnectorRun,
    EntityRecord,
    EvidenceRecord,
    Investigation,
    InvestigationTarget,
    ProvenanceRecord,
    RelationshipRecord,
)


class InvestigationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_investigation(
        self, title: str, description: str | None = None, status: str = "draft"
    ) -> Investigation:
        investigation = Investigation(
            title=title, description=description, status=status
        )
        self.session.add(investigation)
        self.session.commit()
        self.session.refresh(investigation)
        return investigation

    def get_investigation(self, investigation_id: int) -> Investigation | None:
        return self.session.get(Investigation, investigation_id)

    def register_target(
        self,
        investigation_id: int,
        target_type: str,
        value: str,
        *,
        normalized_value: str | None = None,
        notes: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> InvestigationTarget:
        target = InvestigationTarget(
            investigation_id=investigation_id,
            target_type=target_type,
            value=value,
            normalized_value=normalized_value or value,
            notes=notes,
            attributes=attributes or {},
        )
        self.session.add(target)
        self.session.commit()
        self.session.refresh(target)
        return target

    def create_provenance(
        self,
        *,
        source_name: str,
        source_type: str = "manual",
        source_url: str | None = None,
        retrieved_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProvenanceRecord:
        provenance = ProvenanceRecord(
            source_name=source_name,
            source_type=source_type,
            source_url=source_url,
            retrieved_at=retrieved_at,
            metadata=metadata or {},
        )
        self.session.add(provenance)
        self.session.commit()
        self.session.refresh(provenance)
        return provenance

    def add_evidence(
        self,
        *,
        investigation_id: int,
        target_id: int | None = None,
        source_name: str,
        source_url: str | None = None,
        title: str | None = None,
        content: str | None = None,
        content_type: str = "text",
        provenance_id: int | None = None,
        hash_value: str | None = None,
        observed_at: datetime | None = None,
        retrieved_at: datetime | None = None,
        connector_name: str | None = None,
        connector_version: str | None = None,
        raw_source_data: dict[str, Any] | None = None,
        is_verified: bool = False,
        is_immutable: bool = True,
    ) -> EvidenceRecord:
        evidence = EvidenceRecord(
            investigation_id=investigation_id,
            target_id=target_id,
            source_name=source_name,
            source_url=source_url,
            title=title,
            content=content,
            content_type=content_type,
            provenance_id=provenance_id,
            hash_value=hash_value,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            connector_name=connector_name,
            connector_version=connector_version,
            raw_source_data=raw_source_data,
            is_verified=is_verified,
            is_immutable=is_immutable,
        )
        self.session.add(evidence)
        self.session.commit()
        self.session.refresh(evidence)
        return evidence

    def create_entity(
        self,
        *,
        investigation_id: int,
        entity_type: str,
        value: str,
        normalized_value: str | None = None,
        confidence: float = 0.0,
        attributes: dict[str, Any] | None = None,
        target_id: int | None = None,
        provenance_id: int | None = None,
        is_observed: bool = True,
    ) -> EntityRecord:
        entity = EntityRecord(
            investigation_id=investigation_id,
            target_id=target_id,
            entity_type=entity_type,
            value=value,
            normalized_value=normalized_value or value,
            confidence=confidence,
            attributes=attributes or {},
            provenance_id=provenance_id,
            is_observed=is_observed,
        )
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def create_relationship(
        self,
        *,
        investigation_id: int,
        source_entity_id: int,
        target_entity_id: int,
        relation_type: str,
        confidence: float = 0.0,
        attributes: dict[str, Any] | None = None,
        provenance_id: int | None = None,
    ) -> RelationshipRecord:
        relationship = RelationshipRecord(
            investigation_id=investigation_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            confidence=confidence,
            attributes=attributes or {},
            provenance_id=provenance_id,
        )
        self.session.add(relationship)
        self.session.commit()
        self.session.refresh(relationship)
        return relationship

    def create_connector_run(
        self,
        *,
        investigation_id: int,
        target_id: int | None,
        connector_name: str,
        query: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConnectorRun:
        run = ConnectorRun(
            investigation_id=investigation_id,
            target_id=target_id,
            connector_name=connector_name,
            query=query,
            status="queued",
            metadata=metadata or {},
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def update_connector_run(
        self,
        run_id: int,
        *,
        status: str | None = None,
        attempts: int | None = None,
        result_summary: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> ConnectorRun:
        run = self.session.get(ConnectorRun, run_id)
        if run is None:
            raise ValueError(f"Connector run {run_id} not found")
        if status is not None:
            run.status = status
        if attempts is not None:
            run.attempts = attempts
        if result_summary is not None:
            run.result_summary = result_summary
        if error_message is not None:
            run.error_message = error_message
        self.session.commit()
        self.session.refresh(run)
        return run

    def execute_connector_job(
        self,
        *,
        investigation_id: int,
        target_id: int | None,
        connector_name: str,
        query: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConnectorRun:
        from app.services.connector_registry import registry

        run = self.create_connector_run(
            investigation_id=investigation_id,
            target_id=target_id,
            connector_name=connector_name,
            query=query,
            metadata=metadata,
        )
        self.update_connector_run(run.id, status="running", attempts=1)

        try:
            connector = registry.get_connector(connector_name)
            result = connector.execute(query=query)
            self.update_connector_run(
                run.id,
                status="completed",
                attempts=1,
                result_summary={
                    "connector_name": result.connector_name,
                    "query": result.query,
                    "status": result.status,
                    "entity_count": len(result.entities),
                    "evidence_count": len(result.evidence),
                    "warnings": result.warnings,
                },
            )
            return self.session.get(ConnectorRun, run.id)
        except KeyError as exc:
            self.update_connector_run(
                run.id, status="failed", attempts=1, error_message=str(exc)
            )
            raise ValueError(str(exc)) from exc

    def get_graph(self, investigation_id: int) -> dict[str, Any]:
        entities = (
            self.session.execute(
                select(EntityRecord).where(
                    EntityRecord.investigation_id == investigation_id
                )
            )
            .scalars()
            .all()
        )
        relationships = (
            self.session.execute(
                select(RelationshipRecord).where(
                    RelationshipRecord.investigation_id == investigation_id
                )
            )
            .scalars()
            .all()
        )

        return {
            "investigation_id": investigation_id,
            "entities": [
                {
                    "id": entity.id,
                    "entity_type": entity.entity_type,
                    "value": entity.value,
                    "normalized_value": entity.normalized_value,
                    "confidence": entity.confidence,
                    "attributes": entity.attributes,
                    "target_id": entity.target_id,
                    "provenance_id": entity.provenance_id,
                    "created_at": entity.created_at.isoformat(),
                }
                for entity in entities
            ],
            "relationships": [
                {
                    "id": relationship.id,
                    "source_entity_id": relationship.source_entity_id,
                    "target_entity_id": relationship.target_entity_id,
                    "relation_type": relationship.relation_type,
                    "confidence": relationship.confidence,
                    "attributes": relationship.attributes,
                    "provenance_id": relationship.provenance_id,
                    "created_at": relationship.created_at.isoformat(),
                }
                for relationship in relationships
            ],
        }

    def get_investigation_findings(self, investigation_id: int) -> dict[str, Any]:
        evidence = (
            self.session.execute(
                select(EvidenceRecord).where(
                    EvidenceRecord.investigation_id == investigation_id
                )
            )
            .scalars()
            .all()
        )
        entities = (
            self.session.execute(
                select(EntityRecord).where(
                    EntityRecord.investigation_id == investigation_id
                )
            )
            .scalars()
            .all()
        )
        relationships = (
            self.session.execute(
                select(RelationshipRecord).where(
                    RelationshipRecord.investigation_id == investigation_id
                )
            )
            .scalars()
            .all()
        )

        return {
            "investigation_id": investigation_id,
            "evidence": [
                {
                    "id": item.id,
                    "source_name": item.source_name,
                    "source_url": item.source_url,
                    "title": item.title,
                    "content": item.content,
                    "content_type": item.content_type,
                    "observed_at": item.observed_at.isoformat()
                    if item.observed_at
                    else None,
                    "retrieved_at": item.retrieved_at.isoformat()
                    if item.retrieved_at
                    else None,
                    "connector_name": item.connector_name,
                    "connector_version": item.connector_version,
                    "raw_source_data": item.raw_source_data,
                    "hash_value": item.hash_value,
                    "is_verified": item.is_verified,
                    "is_immutable": item.is_immutable,
                    "provenance_id": item.provenance_id,
                    "created_at": item.created_at.isoformat(),
                }
                for item in evidence
            ],
            "entities": [
                {
                    "id": entity.id,
                    "entity_type": entity.entity_type,
                    "value": entity.value,
                    "normalized_value": entity.normalized_value,
                    "confidence": entity.confidence,
                    "attributes": entity.attributes,
                    "target_id": entity.target_id,
                    "provenance_id": entity.provenance_id,
                    "is_observed": entity.is_observed,
                    "created_at": entity.created_at.isoformat(),
                }
                for entity in entities
            ],
            "relationships": [
                {
                    "id": relationship.id,
                    "source_entity_id": relationship.source_entity_id,
                    "target_entity_id": relationship.target_entity_id,
                    "relation_type": relationship.relation_type,
                    "confidence": relationship.confidence,
                    "attributes": relationship.attributes,
                    "provenance_id": relationship.provenance_id,
                    "created_at": relationship.created_at.isoformat(),
                }
                for relationship in relationships
            ],
        }
