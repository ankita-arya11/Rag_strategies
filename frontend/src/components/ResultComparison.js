import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './ResultComparison.css';

const ResultComparison = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState('');
  const [documents, setDocuments] = useState([]);

  const strategies = ['hybrid', 'cross_encoder', 'rrf'];

  const strategyLabels = {
    hybrid: 'Hybrid Search',
    cross_encoder: 'Cross-Encoder',
    rrf: 'RRF'
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Failed to load documents');
    }
  };

  const handleCompare = async () => {
    if (!query.trim()) {
      alert('Please enter a query');
      return;
    }

    setLoading(true);
    const newResults = {};

    try {
      const promises = strategies.map(strategy =>
        api.retrieve(query, strategy, selectedDocument || null, 5)
          .then(result => ({ strategy, result }))
          .catch(error => ({ strategy, error: error.message }))
      );

      const responses = await Promise.all(promises);

      responses.forEach(({ strategy, result, error }) => {
        newResults[strategy] = error ? { error } : result;
      });

      setResults(newResults);
    } catch (err) {
      console.error('Comparison failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Strategy Comparison</h1>
        <p className="page-description">
          Compare retrieval strategies side-by-side to find the best performer for your query.
        </p>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-icon">&#9889;</span>
          Compare Query
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 'var(--space-4)', alignItems: 'start' }}>
          <div>
            <div className="form-group">
              <label className="form-label">Query</label>
              <input
                type="text"
                className="input"
                placeholder="Enter your query to compare across strategies..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleCompare()}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Document (optional)</label>
              <select
                className="select"
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
              >
                <option value="">All documents</option>
                {documents.map(doc => (
                  <option key={doc.document_id} value={doc.document_id}>
                    {doc.filename || doc.document_id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            className="button"
            onClick={handleCompare}
            disabled={loading || !query.trim()}
            style={{ marginTop: '24px' }}
          >
            {loading ? 'Comparing...' : 'Compare All'}
          </button>
        </div>
      </div>

      {Object.keys(results).length > 0 && (
        <div className="comparison-grid">
          {strategies.map(strategy => (
            <div key={strategy} className="strategy-column">
              <div className="strategy-header">
                <h3>{strategyLabels[strategy] || strategy.replace('_', ' ').toUpperCase()}</h3>
                {results[strategy] && !results[strategy].error && (
                  <div className="strategy-metrics">
                    <span className="metric">
                      {results[strategy].latency_ms.toFixed(0)}ms
                    </span>
                    <span className="metric">
                      {results[strategy].total_results} results
                    </span>
                  </div>
                )}
              </div>

              {results[strategy]?.error ? (
                <div className="error-message">
                  {results[strategy].error}
                </div>
              ) : results[strategy]?.results ? (
                <div className="strategy-results">
                  {results[strategy].results.slice(0, 3).map((result, idx) => (
                    <div key={idx} className="comparison-result">
                      <div>
                        <span className="result-rank">#{idx + 1}</span>
                        <span className="result-score">
                          {result.score.toFixed(4)}
                        </span>
                      </div>
                      <div className="result-preview">
                        {result.text.substring(0, 150)}...
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}

      {Object.keys(results).length > 0 && (
        <div className="card" style={{ marginTop: 'var(--space-6)' }}>
          <div className="card-header">
            <span className="card-icon">&#128200;</span>
            Performance Summary
          </div>
          <div className="performance-table">
            <table>
              <thead>
                <tr>
                  <th>Strategy</th>
                  <th>Latency</th>
                  <th>Results</th>
                  <th>Avg Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {strategies.map(strategy => {
                  const data = results[strategy];
                  if (data?.error || !data?.results) return null;

                  const avgScore = data.results.length > 0
                    ? (data.results.reduce((sum, r) => sum + r.score, 0) / data.results.length)
                    : 0;

                  const isFastest = data.latency_ms === Math.min(...strategies
                    .filter(s => results[s]?.latency_ms)
                    .map(s => results[s].latency_ms));

                  const isBestScore = avgScore === Math.max(...strategies
                    .filter(s => results[s]?.results?.length > 0)
                    .map(s => results[s].results.reduce((sum, r) => sum + r.score, 0) / results[s].results.length));

                  return (
                    <tr key={strategy}>
                      <td><strong>{strategyLabels[strategy] || strategy}</strong></td>
                      <td>{data.latency_ms.toFixed(0)}ms</td>
                      <td>{data.total_results}</td>
                      <td>{avgScore.toFixed(4)}</td>
                      <td>
                        {isFastest && <span className="metrics-badge" style={{ background: 'var(--color-success-50)', color: 'var(--color-success-700)', borderColor: 'var(--color-success-100)' }}>Fastest</span>}
                        {isBestScore && <span className="metrics-badge" style={{ background: 'var(--color-warning-50)', color: 'var(--color-warning-600)', borderColor: 'var(--color-warning-100)' }}>Best Score</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultComparison;
