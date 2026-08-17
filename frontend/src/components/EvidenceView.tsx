import React, { useEffect, useState } from 'react';
import type { EvidenceRecord } from '../types';
import { api } from '../api';
import './EvidenceView.css';

export interface EvidenceViewProps {
  investigationId: number;
}

export const EvidenceView: React.FC<EvidenceViewProps> = ({ investigationId }) => {
  const [evidence, setEvidence] = useState<EvidenceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRecord | null>(null);

  useEffect(() => {
    const fetchEvidence = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.evidence.list(investigationId);
        setEvidence(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evidence');
      } finally {
        setLoading(false);
      }
    };

    fetchEvidence();
  }, [investigationId]);

  if (loading) {
    return <div className="loading-state">Loading evidence...</div>;
  }

  if (error) {
    return <div className="error-state">Error: {error}</div>;
  }

  if (evidence.length === 0) {
    return <div className="empty-state">No evidence items collected yet</div>;
  }

  return (
    <div className="evidence-view">
      <div className="evidence-list">
        {evidence.map((item) => (
          <div
            key={item.id}
            className={`evidence-item ${selectedEvidence?.id === item.id ? 'selected' : ''}`}
            onClick={() => setSelectedEvidence(item)}
          >
            <div className="evidence-header">
              <h4>{item.title || item.source_name}</h4>
              {item.connector_name && (
                <span className="evidence-source">{item.connector_name}</span>
              )}
            </div>
            {item.content && <p className="evidence-preview">{item.content}</p>}
            <div className="evidence-meta">
              {item.observed_at && (
                <span className="meta-badge">
                  Observed: {new Date(item.observed_at).toLocaleDateString()}
                </span>
              )}
              {item.is_verified && <span className="meta-badge verified">Verified</span>}
            </div>
          </div>
        ))}
      </div>

      {selectedEvidence && (
        <div className="evidence-detail">
          <div className="detail-panel">
            <h3>{selectedEvidence.title || selectedEvidence.source_name}</h3>

            <div className="detail-section">
              <h4>Provenance</h4>
              <dl className="detail-list">
                <dt>Source</dt>
                <dd>{selectedEvidence.source_name}</dd>
                {selectedEvidence.source_url && (
                  <>
                    <dt>Source URL</dt>
                    <dd>
                      <a
                        href={selectedEvidence.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {selectedEvidence.source_url}
                      </a>
                    </dd>
                  </>
                )}
                {selectedEvidence.connector_name && (
                  <>
                    <dt>Connector</dt>
                    <dd>
                      {selectedEvidence.connector_name}
                      {selectedEvidence.connector_version && `@${selectedEvidence.connector_version}`}
                    </dd>
                  </>
                )}
              </dl>
            </div>

            <div className="detail-section">
              <h4>Timestamps</h4>
              <dl className="detail-list">
                {selectedEvidence.observed_at && (
                  <>
                    <dt>Observed At</dt>
                    <dd>{new Date(selectedEvidence.observed_at).toLocaleString()}</dd>
                  </>
                )}
                {selectedEvidence.retrieved_at && (
                  <>
                    <dt>Retrieved At</dt>
                    <dd>{new Date(selectedEvidence.retrieved_at).toLocaleString()}</dd>
                  </>
                )}
                <dt>Collected At</dt>
                <dd>{new Date(selectedEvidence.created_at).toLocaleString()}</dd>
              </dl>
            </div>

            {selectedEvidence.content && (
              <div className="detail-section">
                <h4>Content</h4>
                <pre className="evidence-content">{selectedEvidence.content}</pre>
              </div>
            )}

            {selectedEvidence.raw_source_data && (
              <div className="detail-section">
                <h4>Raw Data</h4>
                <pre className="evidence-content">
                  {JSON.stringify(selectedEvidence.raw_source_data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
