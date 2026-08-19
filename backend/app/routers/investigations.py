from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models import (
    ConnectorRun,
    EntityRecord,
    EvidenceRecord,
    Investigation,
    InvestigationTarget,
    RelationshipRecord,
)
from app.schemas import (
    ConnectorRunCreate,
    ConnectorRunRead,
    EntityCreate,
    EntityRead,
    EvidenceCreate,
    EvidenceRead,
    GraphResponse,
    InvestigationCreate,
    InvestigationRead,
    InvestigationTargetCreate,
    InvestigationTargetRead,
    RelationshipCreate,
    RelationshipRead,
)
from app.services.intelligence_service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.get("", response_model=list[InvestigationRead])
def list_investigations(
    session: Annotated[Session, Depends(get_db_session)],
) -> list[Investigation]:
    return session.query(Investigation).order_by(Investigation.created_at.desc()).all()


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
def create_investigation(
    payload: InvestigationCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> Investigation:
    service = InvestigationService(session)
    return service.create_investigation(
        payload.title, payload.description, payload.status
    )


@router.get("/{investigation_id}", response_model=InvestigationRead)
def get_investigation(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> Investigation:
    investigation = session.get(Investigation, investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found"
        )
    return investigation


@router.get("/{investigation_id}/targets", response_model=list[InvestigationTargetRead])
def list_targets(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[InvestigationTarget]:
    return (
        session.query(InvestigationTarget)
        .filter(InvestigationTarget.investigation_id == investigation_id)
        .order_by(InvestigationTarget.created_at.desc())
        .all()
    )


@router.post(
    "/{investigation_id}/targets",
    response_model=InvestigationTargetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    investigation_id: int,
    payload: InvestigationTargetCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> InvestigationTarget:
    service = InvestigationService(session)
    return service.register_target(
        investigation_id,
        payload.target_type,
        payload.value,
        normalized_value=payload.normalized_value,
        notes=payload.notes,
        attributes=payload.attributes,
    )


@router.get("/{investigation_id}/entities", response_model=list[EntityRead])
def list_entities(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[EntityRecord]:
    return (
        session.query(EntityRecord)
        .filter(EntityRecord.investigation_id == investigation_id)
        .order_by(EntityRecord.created_at.desc())
        .all()
    )


@router.post(
    "/{investigation_id}/entities",
    response_model=EntityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_entity(
    investigation_id: int,
    payload: EntityCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> EntityRecord:
    service = InvestigationService(session)
    return service.create_entity(
        investigation_id=investigation_id,
        entity_type=payload.entity_type,
        value=payload.value,
        normalized_value=payload.normalized_value,
        confidence=payload.confidence,
        attributes=payload.attributes,
        target_id=payload.target_id,
        provenance_id=payload.provenance_id,
        is_observed=payload.is_observed,
    )


@router.get("/{investigation_id}/evidence", response_model=list[EvidenceRead])
def list_evidence(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[EvidenceRecord]:
    return (
        session.query(EvidenceRecord)
        .filter(EvidenceRecord.investigation_id == investigation_id)
        .order_by(EvidenceRecord.created_at.desc())
        .all()
    )


@router.post(
    "/{investigation_id}/evidence",
    response_model=EvidenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence(
    investigation_id: int,
    payload: EvidenceCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> EvidenceRecord:
    service = InvestigationService(session)
    return service.add_evidence(
        investigation_id=investigation_id,
        target_id=payload.target_id,
        source_name=payload.source_name,
        source_url=payload.source_url,
        title=payload.title,
        content=payload.content,
        content_type=payload.content_type,
        provenance_id=payload.provenance_id,
        hash_value=payload.hash_value,
        observed_at=payload.observed_at,
        retrieved_at=payload.retrieved_at,
        connector_name=payload.connector_name,
        connector_version=payload.connector_version,
        raw_source_data=payload.raw_source_data,
        is_verified=payload.is_verified,
        is_immutable=payload.is_immutable,
    )


@router.get("/{investigation_id}/relationships", response_model=list[RelationshipRead])
def list_relationships(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[RelationshipRecord]:
    return (
        session.query(RelationshipRecord)
        .filter(RelationshipRecord.investigation_id == investigation_id)
        .order_by(RelationshipRecord.created_at.desc())
        .all()
    )


@router.post(
    "/{investigation_id}/relationships",
    response_model=RelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship(
    investigation_id: int,
    payload: RelationshipCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> RelationshipRecord:
    service = InvestigationService(session)
    return service.create_relationship(
        investigation_id=investigation_id,
        source_entity_id=payload.source_entity_id,
        target_entity_id=payload.target_entity_id,
        relation_type=payload.relation_type,
        confidence=payload.confidence,
        attributes=payload.attributes,
        provenance_id=payload.provenance_id,
    )


@router.get("/{investigation_id}/graph", response_model=GraphResponse)
def get_graph(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> GraphResponse:
    service = InvestigationService(session)
    data = service.get_graph(investigation_id)
    return GraphResponse(**data)


@router.post(
    "/{investigation_id}/connector-runs",
    response_model=ConnectorRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_connector_run(
    investigation_id: int,
    payload: ConnectorRunCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> Any:
    investigation = session.get(Investigation, investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    if payload.target_id is not None:
        target = session.get(InvestigationTarget, payload.target_id)
        if target is None or target.investigation_id != investigation_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target not found",
            )

    service = InvestigationService(session)
    return service.create_connector_run(
        investigation_id=investigation_id,
        target_id=payload.target_id,
        connector_name=payload.connector_name,
        query=payload.query,
        metadata=payload.metadata,
    )


@router.post(
    "/{investigation_id}/connector-runs/{run_id}/execute",
    response_model=ConnectorRunRead,
)
def execute_connector_run(
    investigation_id: int,
    run_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> ConnectorRun:
    investigation = session.get(Investigation, investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    run = session.get(ConnectorRun, run_id)
    if run is None or run.investigation_id != investigation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector run not found",
        )

    if run.status not in {"queued", "failed"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Connector run cannot be executed from status '{run.status}'",
        )

    service = InvestigationService(session)

    try:
        return service.execute_connector_job(
            investigation_id=investigation_id,
            target_id=run.target_id,
            connector_name=run.connector_name,
            query=run.query,
            metadata=run.run_metadata,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{investigation_id}/connector-runs", response_model=list[ConnectorRunRead])
def list_connector_runs(
    investigation_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[Any]:
    return (
        session.query(ConnectorRun)
        .filter(ConnectorRun.investigation_id == investigation_id)
        .order_by(ConnectorRun.created_at.desc())
        .all()
    )


@router.put("/{investigation_id}", response_model=InvestigationRead)
def update_investigation(
    investigation_id: int,
    payload: dict[str, Any],
    session: Annotated[Session, Depends(get_db_session)],
) -> Investigation:
    investigation = session.get(Investigation, investigation_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found"
        )
    if "title" in payload:
        investigation.title = payload["title"]
    if "description" in payload:
        investigation.description = payload["description"]
    if "status" in payload:
        investigation.status = payload["status"]
    session.commit()
    session.refresh(investigation)
    return investigation


@router.get(
    "/{investigation_id}/targets/{target_id}", response_model=InvestigationTargetRead
)
def get_target(
    investigation_id: int,
    target_id: int,
    session: Annotated[Session, Depends(get_db_session)],
) -> InvestigationTarget:
    target = session.get(InvestigationTarget, target_id)
    if target is None or target.investigation_id != investigation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target not found"
        )
    return target


@router.put(
    "/{investigation_id}/targets/{target_id}", response_model=InvestigationTargetRead
)
def update_target(
    investigation_id: int,
    target_id: int,
    payload: dict[str, Any],
    session: Annotated[Session, Depends(get_db_session)],
) -> InvestigationTarget:
    target = session.get(InvestigationTarget, target_id)
    if target is None or target.investigation_id != investigation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target not found"
        )
    if "value" in payload:
        target.value = payload["value"]
    if "normalized_value" in payload:
        target.normalized_value = payload["normalized_value"]
    if "notes" in payload:
        target.notes = payload["notes"]
    if "attributes" in payload:
        target.attributes = payload["attributes"]
    session.commit()
    session.refresh(target)
    return target
