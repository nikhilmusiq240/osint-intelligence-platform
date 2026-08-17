/**
 * TypeScript types matching backend API schemas
 * Generated from backend/app/schemas.py
 */

// Investigation types
export interface Investigation {
  id: number;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface InvestigationCreate {
  title: string;
  description?: string | null;
  status?: string;
}

// Investigation Target types
export interface InvestigationTarget {
  id: number;
  investigation_id: number;
  target_type: string;
  value: string;
  normalized_value: string | null;
  notes: string | null;
  attributes: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface InvestigationTargetCreate {
  target_type: string;
  value: string;
  normalized_value?: string | null;
  notes?: string | null;
  attributes?: Record<string, unknown> | null;
}

// Evidence types
export interface EvidenceRecord {
  id: number;
  investigation_id: number;
  source_name: string;
  source_url: string | null;
  title: string | null;
  content: string | null;
  content_type: string;
  hash_value: string | null;
  captured_at: string | null;
  observed_at: string | null;
  retrieved_at: string | null;
  connector_name: string | null;
  connector_version: string | null;
  raw_source_data: Record<string, unknown> | null;
  target_id: number | null;
  entity_id: number | null;
  provenance_id: number | null;
  is_verified: boolean;
  is_immutable: boolean;
  created_at: string;
}

export interface EvidenceCreate {
  source_name: string;
  source_url?: string | null;
  title?: string | null;
  content?: string | null;
  content_type?: string;
  hash_value?: string | null;
  captured_at?: string | null;
  observed_at?: string | null;
  retrieved_at?: string | null;
  connector_name?: string | null;
  connector_version?: string | null;
  raw_source_data?: Record<string, unknown> | null;
  target_id?: number | null;
  entity_id?: number | null;
  provenance_id?: number | null;
  is_verified?: boolean;
  is_immutable?: boolean;
}

// Entity types
export interface EntityRecord {
  id: number;
  investigation_id: number;
  entity_type: string;
  value: string;
  normalized_value: string | null;
  confidence: number;
  attributes: Record<string, unknown> | null;
  target_id: number | null;
  provenance_id: number | null;
  is_observed: boolean;
  created_at: string;
  updated_at: string;
}

export interface EntityCreate {
  entity_type: string;
  value: string;
  normalized_value?: string | null;
  confidence?: number;
  attributes?: Record<string, unknown> | null;
  target_id?: number | null;
  provenance_id?: number | null;
  is_observed?: boolean;
}

// Relationship types
export interface RelationshipRecord {
  id: number;
  investigation_id: number;
  source_entity_id: number;
  target_entity_id: number;
  relation_type: string;
  confidence: number;
  attributes: Record<string, unknown> | null;
  provenance_id: number | null;
  created_at: string;
}

export interface RelationshipCreate {
  source_entity_id: number;
  target_entity_id: number;
  relation_type: string;
  confidence?: number;
  attributes?: Record<string, unknown> | null;
  provenance_id?: number | null;
}

// Graph types
export interface GraphNode {
  id: number;
  entity_type: string;
  value: string;
  normalized_value: string | null;
  confidence: number;
  attributes: Record<string, unknown> | null;
  target_id: number | null;
  provenance_id: number | null;
  created_at: string;
}

export interface GraphEdge {
  id: number;
  source_entity_id: number;
  target_entity_id: number;
  relation_type: string;
  confidence: number;
  attributes: Record<string, unknown> | null;
  provenance_id: number | null;
  created_at: string;
}

export interface GraphResponse {
  investigation_id: number;
  entities: GraphNode[];
  relationships: GraphEdge[];
}

// Connector Run types
export interface ConnectorRun {
  id: number;
  investigation_id: number;
  target_id: number | null;
  connector_name: string;
  query: string;
  status: string;
  attempts: number;
  metadata: Record<string, unknown> | null;
  result_summary: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ConnectorRunCreate {
  connector_name: string;
  query: string;
  status?: string;
  attempts?: number;
  metadata?: Record<string, unknown> | null;
  target_id?: number | null;
}

// Health check types
export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
}

// API response types
export interface ApiError {
  detail: string;
}
