from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import EntityRecord, EvidenceRecord, Investigation, InvestigationJob


class InvestigationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_investigation(
        self, title: str, description: str | None = None
    ) -> Investigation:
        investigation = Investigation(
            title=title, description=description, status="draft"
        )
        self.session.add(investigation)
        self.session.commit()
        self.session.refresh(investigation)
        return investigation

    def create_job(
        self,
        investigation_id: int,
        connector_name: str,
        query: str,
        job_metadata: dict[str, Any] | None = None,
    ) -> InvestigationJob:
        job = InvestigationJob(
            investigation_id=investigation_id,
            connector_name=connector_name,
            query=query,
            job_metadata=job_metadata or {},
            status="queued",
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def create_entity(
        self, investigation_id: int, entity_type: str, value: str, **kwargs: Any
    ) -> EntityRecord:
        entity = EntityRecord(
            investigation_id=investigation_id,
            entity_type=entity_type,
            value=value,
            **kwargs,
        )
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def create_evidence(
        self,
        investigation_id: int,
        source_name: str,
        *,
        content: str | None = None,
        **kwargs: Any,
    ) -> EvidenceRecord:
        evidence = EvidenceRecord(
            investigation_id=investigation_id,
            source_name=source_name,
            content=content,
            **kwargs,
        )
        self.session.add(evidence)
        self.session.commit()
        self.session.refresh(evidence)
        return evidence
