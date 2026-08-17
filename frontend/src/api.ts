/**
 * API Client for OSINT Intelligence Platform Backend
 * Handles all HTTP communication with the backend
 */

import type {
  Investigation,
  InvestigationCreate,
  InvestigationTarget,
  InvestigationTargetCreate,
  EvidenceRecord,
  EvidenceCreate,
  EntityRecord,
  EntityCreate,
  RelationshipRecord,
  RelationshipCreate,
  GraphResponse,
  ConnectorRun,
  ConnectorRunCreate,
  HealthResponse,
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Health check
  health: async (): Promise<HealthResponse> => {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthResponse>(response);
  },

  // Investigations
  investigations: {
    list: async (): Promise<Investigation[]> => {
      const response = await fetch(`${API_BASE}/investigations`);
      return handleResponse<Investigation[]>(response);
    },

    create: async (payload: InvestigationCreate): Promise<Investigation> => {
      const response = await fetch(`${API_BASE}/investigations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return handleResponse<Investigation>(response);
    },

    get: async (id: number): Promise<Investigation> => {
      const response = await fetch(`${API_BASE}/investigations/${id}`);
      return handleResponse<Investigation>(response);
    },

    update: async (id: number, payload: Partial<InvestigationCreate>): Promise<Investigation> => {
      const response = await fetch(`${API_BASE}/investigations/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return handleResponse<Investigation>(response);
    },
  },

  // Investigation Targets
  targets: {
    list: async (investigationId: number): Promise<InvestigationTarget[]> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/targets`);
      return handleResponse<InvestigationTarget[]>(response);
    },

    create: async (
      investigationId: number,
      payload: InvestigationTargetCreate
    ): Promise<InvestigationTarget> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/targets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return handleResponse<InvestigationTarget>(response);
    },

    get: async (investigationId: number, targetId: number): Promise<InvestigationTarget> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/targets/${targetId}`
      );
      return handleResponse<InvestigationTarget>(response);
    },

    update: async (
      investigationId: number,
      targetId: number,
      payload: Partial<InvestigationTargetCreate>
    ): Promise<InvestigationTarget> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/targets/${targetId}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );
      return handleResponse<InvestigationTarget>(response);
    },
  },

  // Evidence
  evidence: {
    list: async (investigationId: number): Promise<EvidenceRecord[]> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/evidence`);
      return handleResponse<EvidenceRecord[]>(response);
    },

    create: async (
      investigationId: number,
      payload: EvidenceCreate
    ): Promise<EvidenceRecord> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/evidence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return handleResponse<EvidenceRecord>(response);
    },
  },

  // Entities
  entities: {
    list: async (investigationId: number): Promise<EntityRecord[]> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/entities`);
      return handleResponse<EntityRecord[]>(response);
    },

    create: async (investigationId: number, payload: EntityCreate): Promise<EntityRecord> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return handleResponse<EntityRecord>(response);
    },
  },

  // Relationships
  relationships: {
    list: async (investigationId: number): Promise<RelationshipRecord[]> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/relationships`
      );
      return handleResponse<RelationshipRecord[]>(response);
    },

    create: async (
      investigationId: number,
      payload: RelationshipCreate
    ): Promise<RelationshipRecord> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/relationships`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );
      return handleResponse<RelationshipRecord>(response);
    },
  },

  // Graph
  graph: {
    get: async (investigationId: number): Promise<GraphResponse> => {
      const response = await fetch(`${API_BASE}/investigations/${investigationId}/graph`);
      return handleResponse<GraphResponse>(response);
    },
  },

  // Connector Runs
  connectorRuns: {
    list: async (investigationId: number): Promise<ConnectorRun[]> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/connector-runs`
      );
      return handleResponse<ConnectorRun[]>(response);
    },

    create: async (
      investigationId: number,
      payload: ConnectorRunCreate
    ): Promise<ConnectorRun> => {
      const response = await fetch(
        `${API_BASE}/investigations/${investigationId}/connector-runs`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );
      return handleResponse<ConnectorRun>(response);
    },
  },
};
