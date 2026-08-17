import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Investigation Workspace</p>
          <h1>OSINT Intelligence Platform</h1>
        </div>
        <button type="button" className="primary-button">
          New investigation
        </button>
      </header>

      <section className="overview-grid">
        <article className="panel stat-panel">
          <span>Active investigations</span>
          <strong>12</strong>
        </article>
        <article className="panel stat-panel">
          <span>Queued jobs</span>
          <strong>4</strong>
        </article>
        <article className="panel stat-panel">
          <span>Evidence items</span>
          <strong>381</strong>
        </article>
      </section>

      <section className="panel layout-grid">
        <div>
          <h2>Investigation pipeline</h2>
          <ul className="pipeline-list">
            <li><span className="status-dot live" /> Threat actor cluster</li>
            <li><span className="status-dot pending" /> Domain enrichment</li>
            <li><span className="status-dot review" /> Artifact validation</li>
          </ul>
        </div>
        <div>
          <h2>Connectors</h2>
          <ul className="connector-list">
            <li>Domain intelligence</li>
            <li>Public records</li>
            <li>Social signals</li>
            <li>Artifact analysis</li>
          </ul>
        </div>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
