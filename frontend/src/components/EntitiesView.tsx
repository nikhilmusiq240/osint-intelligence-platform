import React, { useEffect, useState } from 'react';
import type { GraphResponse, EntityRecord, RelationshipRecord } from '../types';
import { api } from '../api';
import './EntitiesView.css';

export interface EntitiesViewProps {
  investigationId: number;
}

export const EntitiesView: React.FC<EntitiesViewProps> = ({ investigationId }) => {
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [entities, setEntities] = useState<EntityRecord[]>([]);
  const [relationships, setRelationships] = useState<RelationshipRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<EntityRecord | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [graphData, entitiesData, relationshipsData] = await Promise.all([
          api.graph.get(investigationId),
          api.entities.list(investigationId),
          api.relationships.list(investigationId),
        ]);
        setGraph(graphData);
        setEntities(entitiesData);
        setRelationships(relationshipsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load graph data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [investigationId]);

  if (loading) {
    return <div className="loading-state">Loading entities and relationships...</div>;
  }

  if (error) {
    return <div className="error-state">Error: {error}</div>;
  }

  if (entities.length === 0) {
    return <div className="empty-state">No entities discovered yet</div>;
  }

  return (
    <div className="entities-view">
      <div className="entities-list">
        <h3>Entities ({entities.length})</h3>
        <div className="entity-items">
          {entities.map((entity) => (
            <div
              key={entity.id}
              className={`entity-card ${selectedEntity?.id === entity.id ? 'selected' : ''}`}
              onClick={() => setSelectedEntity(entity)}
            >
              <div className="entity-type-badge">{entity.entity_type}</div>
              <h4>{entity.value}</h4>
              {entity.normalized_value && (
                <p className="entity-normalized">{entity.normalized_value}</p>
              )}
              <div className="entity-confidence">
                Confidence: <span className="confidence-value">{(entity.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedEntity && (
        <div className="entity-detail">
          <div className="detail-card">
            <h3>{selectedEntity.value}</h3>
            <div className="detail-row">
              <span className="detail-label">Type:</span>
              <span className="detail-value">{selectedEntity.entity_type}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Confidence:</span>
              <span className="detail-value">{(selectedEntity.confidence * 100).toFixed(0)}%</span>
            </div>
            {selectedEntity.normalized_value && (
              <div className="detail-row">
                <span className="detail-label">Normalized:</span>
                <span className="detail-value">{selectedEntity.normalized_value}</span>
              </div>
            )}
            {selectedEntity.attributes && Object.keys(selectedEntity.attributes).length > 0 && (
              <div className="detail-section">
                <h4>Attributes</h4>
                <pre className="detail-json">
                  {JSON.stringify(selectedEntity.attributes, null, 2)}
                </pre>
              </div>
            )}

            {relationships.length > 0 && (
              <div className="detail-section">
                <h4>Relationships</h4>
                <div className="relationships-list">
                  {relationships
                    .filter(
                      (rel) =>
                        rel.source_entity_id === selectedEntity.id ||
                        rel.target_entity_id === selectedEntity.id
                    )
                    .map((rel) => {
                      const isSource = rel.source_entity_id === selectedEntity.id;
                      const otherEntityId = isSource
                        ? rel.target_entity_id
                        : rel.source_entity_id;
                      const otherEntity = entities.find((e) => e.id === otherEntityId);
                      return (
                        <div key={rel.id} className="relationship-item">
                          {isSource ? (
                            <>
                              <span className="rel-entity">{selectedEntity.value}</span>
                              <span className="rel-type">{rel.relation_type}</span>
                              <span className="rel-entity">
                                {otherEntity?.value || `Entity ${otherEntityId}`}
                              </span>
                            </>
                          ) : (
                            <>
                              <span className="rel-entity">
                                {otherEntity?.value || `Entity ${otherEntityId}`}
                              </span>
                              <span className="rel-type">{rel.relation_type}</span>
                              <span className="rel-entity">{selectedEntity.value}</span>
                            </>
                          )}
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="relationships-overview">
        <h3>Relationships ({relationships.length})</h3>
        <div className="relationships-table">
          {relationships.length === 0 ? (
            <p className="no-data">No relationships defined</p>
          ) : (
            relationships.map((rel) => {
              const sourceEntity = entities.find((e) => e.id === rel.source_entity_id);
              const targetEntity = entities.find((e) => e.id === rel.target_entity_id);
              return (
                <div key={rel.id} className="table-row">
                  <div className="table-cell">
                    {sourceEntity?.value || `Entity ${rel.source_entity_id}`}
                  </div>
                  <div className="table-cell relation">{rel.relation_type}</div>
                  <div className="table-cell">
                    {targetEntity?.value || `Entity ${rel.target_entity_id}`}
                  </div>
                  <div className="table-cell confidence">
                    {(rel.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
