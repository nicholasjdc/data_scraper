import React, { useState } from 'react';
import { analyzeWithAI } from '../services/api';
import type { AIAnalysisResponse, AIAnalysisClaim } from '../types/api';
import './AIAnalysisPanel.css';

interface Props {
  fetchIds: string[];
}

const ClaimCard: React.FC<{ claim: AIAnalysisClaim }> = ({ claim }) => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  return (
    <div className={`claim-card ${claim.verified ? 'claim-verified' : 'claim-unverified'}`}>
      <p className="claim-text">{claim.text}</p>
      <div className="claim-citation">
        <span className="citation-badge">
          {claim.series_id} • {claim.date} • {claim.value}
        </span>
        <a
          href={`${apiBase}/api/v1/provenance/${claim.fetch_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="citation-link"
          title={`fetch_id: ${claim.fetch_id}`}
        >
          {claim.verified ? '✓ verified' : '⚠ unverified'}
        </a>
        {!claim.verified && (
          <span className="citation-note" title={claim.verification_note}>
            {claim.verification_note}
          </span>
        )}
      </div>
    </div>
  );
};

const AIAnalysisPanel: React.FC<Props> = ({ fetchIds }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AIAnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    if (fetchIds.length === 0) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeWithAI({
        fetch_ids: fetchIds,
        question: question.trim() || undefined,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'AI analysis failed');
    } finally {
      setLoading(false);
    }
  };

  if (fetchIds.length === 0) return null;

  return (
    <div className="ai-panel">
      <div className="ai-panel-header">
        <h3 className="ai-panel-title">AI Analysis</h3>
        <p className="ai-panel-subtitle">
          Claude will analyze the {fetchIds.length} fetched series and cite specific values from the source records.
        </p>
      </div>

      <div className="ai-panel-controls">
        <input
          type="text"
          className="ai-question-input"
          placeholder="Optional question (e.g. What trends do you see in inflation vs unemployment?)"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && handleAnalyze()}
          disabled={loading}
        />
        <button
          className="ai-analyze-button"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? 'Analyzing…' : 'Analyze with AI'}
        </button>
      </div>

      {loading && (
        <div className="ai-loading">
          <div className="ai-loading-spinner" />
          <span>Claude is fetching data and building analysis…</span>
        </div>
      )}

      {error && (
        <div className="ai-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="ai-result">
          <div className="ai-result-meta">
            <span className="ai-model-badge">{result.model_id}</span>
            <span className={`ai-verified-badge ${result.verified ? 'all-verified' : 'some-unverified'}`}>
              {result.verified ? '✓ all claims verified' : '⚠ some claims unverified'}
            </span>
            <a
              href={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/provenance/${result.analysis_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="ai-audit-link"
            >
              view audit record ↗
            </a>
          </div>

          <div className="ai-summary">
            <p>{result.summary}</p>
          </div>

          {result.claims.length > 0 && (
            <div className="ai-claims">
              <h4 className="ai-claims-title">Cited claims</h4>
              {result.claims.map((claim, i) => (
                <ClaimCard key={i} claim={claim} />
              ))}
            </div>
          )}

          {result.data_gaps.length > 0 && (
            <div className="ai-gaps">
              <h4 className="ai-gaps-title">Data gaps noted by AI</h4>
              <ul className="ai-gaps-list">
                {result.data_gaps.map((gap, i) => (
                  <li key={i}>{gap}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="ai-source-trace">
            <span className="ai-source-trace-label">Based on {result.input_fetch_ids.length} fetch record(s):</span>
            <div className="ai-fetch-ids">
              {result.input_fetch_ids.map((fid) => (
                <code key={fid} className="ai-fetch-id">{fid.slice(0, 8)}…</code>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysisPanel;
