import React, { useState } from 'react';
import './ProvenanceBadge.css';

interface Props {
  fetchId: string;
  fetchedAt: string;
  source: string;
  seriesId: string;
  latencyMs?: number;
}

function formatFetchedAt(iso: string): string {
  try {
    const d = new Date(iso);
    const today = new Date();
    const isToday =
      d.getFullYear() === today.getFullYear() &&
      d.getMonth() === today.getMonth() &&
      d.getDate() === today.getDate();
    const time = d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
      hour12: false,
    });
    if (isToday) return `${time} UTC`;
    return `${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })} ${time} UTC`;
  } catch {
    return iso;
  }
}

const ProvenanceBadge: React.FC<Props> = ({ fetchId, fetchedAt, source, seriesId, latencyMs }) => {
  const [expanded, setExpanded] = useState(false);

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const rawUrl = `${apiBase}/api/v1/provenance/${fetchId}`;

  return (
    <span className="provenance-badge-wrapper">
      <button
        className="provenance-badge"
        onClick={() => setExpanded((v) => !v)}
        title="Show provenance details"
      >
        <span className="badge-source">{source.toUpperCase()}:{seriesId}</span>
        <span className="badge-sep">•</span>
        <span className="badge-time">fetched {formatFetchedAt(fetchedAt)}</span>
        <span className="badge-chevron">{expanded ? '▾' : '▸'}</span>
      </button>

      {expanded && (
        <div className="provenance-detail">
          <div className="provenance-detail-row">
            <span className="provenance-label">fetch_id</span>
            <code className="provenance-value">{fetchId}</code>
          </div>
          <div className="provenance-detail-row">
            <span className="provenance-label">fetched_at</span>
            <code className="provenance-value">{fetchedAt}</code>
          </div>
          {latencyMs !== undefined && (
            <div className="provenance-detail-row">
              <span className="provenance-label">latency</span>
              <code className="provenance-value">{latencyMs} ms</code>
            </div>
          )}
          <div className="provenance-detail-row">
            <a
              href={rawUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="provenance-raw-link"
            >
              view raw record ↗
            </a>
          </div>
        </div>
      )}
    </span>
  );
};

export default ProvenanceBadge;
