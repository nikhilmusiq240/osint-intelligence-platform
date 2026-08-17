import React, { useEffect, useState } from 'react';
import type { Investigation } from '../types';
import { api } from '../api';
import './InvestigationList.css';

export interface InvestigationListProps {
  onSelectInvestigation: (investigation: Investigation) => void;
}

export const InvestigationList: React.FC<InvestigationListProps> = ({
  onSelectInvestigation,
}) => {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvestigations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.investigations.list();
        setInvestigations(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load investigations');
      } finally {
        setLoading(false);
      }
    };

    fetchInvestigations();
  }, []);

  if (loading) {
    return (
      <div className="investigation-list">
        <div className="loading-state">
          <p>Loading investigations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="investigation-list">
        <div className="error-state">
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  if (investigations.length === 0) {
    return (
      <div className="investigation-list">
        <div className="empty-state">
          <p>No investigations yet</p>
          <p className="empty-state-hint">Create a new investigation to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="investigation-list">
      <ul className="investigation-items">
        {investigations.map((investigation) => (
          <li key={investigation.id}>
            <button
              className="investigation-item"
              onClick={() => onSelectInvestigation(investigation)}
            >
              <div className="investigation-header">
                <h3>{investigation.title}</h3>
                <span className={`status-badge status-${investigation.status}`}>
                  {investigation.status}
                </span>
              </div>
              {investigation.description && (
                <p className="investigation-description">{investigation.description}</p>
              )}
              <div className="investigation-meta">
                <span className="meta-date">
                  {new Date(investigation.created_at).toLocaleDateString()}
                </span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
