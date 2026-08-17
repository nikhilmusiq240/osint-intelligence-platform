from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    status: str = "draft"


class InvestigationCreate(InvestigationBase):
    pass


class InvestigationRead(InvestigationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvestigationTargetBase(BaseModel):
    target_type: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=255)
    normalized_value: str | None = None
    notes: str | None = None
    attributes: dict[str, Any] | None = None


class InvestigationTargetCreate(InvestigationTargetBase):
    pass


class InvestigationTargetRead(InvestigationTargetBase):
    id: int
    investigation_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProvenanceBase(BaseModel):
    source_name: str
    source_type: str = "manual"
    source_url: str | None = None
    retrieved_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class ProvenanceCreate(ProvenanceBase):
    pass


class ProvenanceRead(ProvenanceBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class JobBase(BaseModel):
    connector_name: str
    query: str
    job_metadata: dict[str, Any] | None = None


class JobCreate(JobBase):
    investigation_id: int


class JobRead(JobBase):
    id: int
    investigation_id: int
    status: str
    attempts: int
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class EntityBase(BaseModel):
    entity_type: str
    value: str
    normalized_value: str | None = None
    confidence: float = 0.0
    attributes: dict[str, Any] | None = None
    target_id: int | None = None
    provenance_id: int | None = None
    is_observed: bool = True


class EntityCreate(EntityBase):
    investigation_id: int | None = None


class EntityRead(EntityBase):
    id: int
    investigation_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RelationshipBase(BaseModel):
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    confidence: float = 0.0
    attributes: dict[str, Any] | None = None
    provenance_id: int | None = None


class RelationshipCreate(RelationshipBase):
    investigation_id: int | None = None


class RelationshipRead(RelationshipBase):
    id: int
    investigation_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceBase(BaseModel):
    source_name: str
    source_url: str | None = None
    title: str | None = None
    content: str | None = None
    content_type: str = "text"
    hash_value: str | None = None
    captured_at: datetime | None = None
    observed_at: datetime | None = None
    retrieved_at: datetime | None = None
    connector_name: str | None = None
    connector_version: str | None = None
    raw_source_data: dict[str, Any] | None = None
    target_id: int | None = None
    entity_id: int | None = None
    provenance_id: int | None = None
    is_verified: bool = False
    is_immutable: bool = True


class EvidenceCreate(EvidenceBase):
    investigation_id: int | None = None


class EvidenceRead(EvidenceBase):
    id: int
    investigation_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectorRunBase(BaseModel):
    connector_name: str
    query: str
    status: str = "queued"
    attempts: int = 0
    metadata: dict[str, Any] | None = Field(default=None, alias="run_metadata")
    result_summary: dict[str, Any] | None = None
    error_message: str | None = None


class ConnectorRunCreate(ConnectorRunBase):
    investigation_id: int | None = None
    target_id: int | None = None


class ConnectorRunRead(ConnectorRunBase):
    id: int
    investigation_id: int
    target_id: int | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class GraphNode(BaseModel):
    id: int
    entity_type: str
    value: str
    normalized_value: str | None = None
    confidence: float = 0.0
    attributes: dict[str, Any] | None = None
    target_id: int | None = None
    provenance_id: int | None = None
    created_at: datetime


class GraphEdge(BaseModel):
    id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    confidence: float = 0.0
    attributes: dict[str, Any] | None = None
    provenance_id: int | None = None
    created_at: datetime


class GraphResponse(BaseModel):
    investigation_id: int
    entities: list[GraphNode]
    relationships: list[GraphEdge]


class ConnectorInfo(BaseModel):
    name: str
    category: str
    description: str


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
