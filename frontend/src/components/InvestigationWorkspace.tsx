import React, { useEffect, useState } from 'react';
import type { Investigation } from '../types';
import { api } from '../api';
import { EvidenceView } from './EvidenceView';
import { EntitiesView } from './EntitiesView';
import { ConnectorRunsView } from './ConnectorRunsView';
import './InvestigationWorkspace.css';

export interface InvestigationWorkspaceProps {
  investigation: Investigation;
  onBack: () => void;
}

type TabType = 'overview' | 'targets' | 'evidence' | 'entities' | 'runs';

export const InvestigationWorkspace: React.FC<InvestigationWorkspaceProps> = ({
  investigation,
  onBack,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
  }, [activeTab]);

  return (
    <div className="investigation-workspace">
      <div className="workspace-header">
        <div className="workspace-title-section">
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
          <div>
            <h2>{investigation.title}</h2>
            {investigation.description && (
              <p className="workspace-description">{investigation.description}</p>
            )}
          </div>
        </div>
        <div className="workspace-meta">
          <span className={`status-badge status-${investigation.status}`}>
            {investigation.status}
          </span>
          <span className="meta-date">
            {new Date(investigation.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="workspace-tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'targets' ? 'active' : ''}`}
          onClick={() => setActiveTab('targets')}
        >
          Targets
        </button>
        <button
          className={`tab-button ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Evidence
        </button>
        <button
          className={`tab-button ${activeTab === 'entities' ? 'active' : ''}`}
          onClick={() => setActiveTab('entities')}
        >
          Entities & Relationships
        </button>
        <button
          className={`tab-button ${activeTab === 'runs' ? 'active' : ''}`}
          onClick={() => setActiveTab('runs')}
        >
          Connector Runs
        </button>
      </div>

      <div className="workspace-content">
        {error && <div className="error-banner">{error}</div>}

        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="panel">
              <h3>Investigation Details</h3>
              <dl className="details-list">
                <dt>Status</dt>
                <dd>{investigation.status}</dd>
                <dt>Created</dt>
                <dd>{new Date(investigation.created_at).toLocaleString()}</dd>
                <dt>Updated</dt>
                <dd>{new Date(investigation.updated_at).toLocaleString()}</dd>
              </dl>
            </div>
          </div>
        )}

        {activeTab === 'targets' && (
          <TargetsTab investigationId={investigation.id} />
        )}

        {activeTab === 'evidence' && (
          <EvidenceView investigationId={investigation.id} />
        )}

        {activeTab === 'entities' && (
          <EntitiesView investigationId={investigation.id} />
        )}

        {activeTab === 'runs' && (
          <ConnectorRunsView investigationId={investigation.id} />
        )}
      </div>
    </div>
  );
};

const TargetsTab: React.FC<{ investigationId: number }> = ({ investigationId }) => {
  const [targets, setTargets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTargets = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.targets.list(investigationId);
        setTargets(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load targets');
      } finally {
        setLoading(false);
      }
    };

    fetchTargets();
  }, [investigationId]);

  if (loading) {
    return <div className="loading-state">Loading targets...</div>;
  }

  if (error) {
    return <div className="error-state">Error: {error}</div>;
  }

  if (targets.length === 0) {
    return <div className="empty-state">No targets added yet</div>;
  }

  return (
    <div className="targets-view">
      <div className="items-grid">
        {targets.map((target) => (
          <div key={target.id} className="panel item-card">
            <h4>{target.value}</h4>
            <p className="item-type">{target.target_type}</p>
            {target.notes && <p className="item-notes">{target.notes}</p>}
            <p className="item-meta">
              {new Date(target.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
