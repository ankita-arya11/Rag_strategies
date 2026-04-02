import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAppContext } from '../context/AppContext';
import MetricsDisplay from '../components/MetricsDisplay';
import './RetrievalStrategies.css';

const RetrievalStrategies = () => {
  const { 
    documents, 
    setDocuments,
    retrievalResults,
    setRetrievalResults,
    lastQuery,
    setLastQuery,
    selectedDocument,
    setSelectedDocument,
    collections,
    setCollections
  } = useAppContext();
  
  const [selectedStrategy, setSelectedStrategy] = useState('hybrid');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [retrievalMetrics, setRetrievalMetrics] = useState(null);

  const strategies = [
    { value: 'hybrid', label: 'Hybrid Search', description: 'Combines dense vector and sparse BM25 search' },
    { value: 'cross_encoder', label: 'Cross-Encoder Reranking', description: 'Vector search with cross-encoder reranking' },
    { value: 'rrf', label: 'Reciprocal Rank Fusion (RRF)', description: 'Rank-based fusion of multiple retrieval methods' }
  ];

  useEffect(() => {
    if (documents.length === 0) {
      loadDocuments();
    }
    if (collections.length === 0) {
      loadCollections();
    }
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      setError('Failed to load documents');
    }
  };

  const loadCollections = async () => {
    try {
      const response = await fetch('http://localhost:8000/collections');
      const data = await response.json();
      setCollections(data.collections || []);
    } catch (err) {
      console.error('Failed to load collections:', err);
    }
  };

  const handleRetrieve = async () => {
    if (!lastQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError('');
    setRetrievalResults([]);

    try {
      const result = await api.retrieve(
        lastQuery,
        selectedStrategy,
        selectedDocument || null,
        topK
      );

      setRetrievalResults(result.results);
      setRetrievalMetrics({
        strategy: selectedStrategy,
        latency: result.latency_ms,
        totalResults: result.total_results
      });
    } catch (err) {
      setError(err.message || 'Retrieval failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRetrieve();
    }
  };

  const currentStrategy = strategies.find(s => s.value === selectedStrategy);

  const highlightQuery = (text, query) => {
    if (!query || !text) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ?
        <mark key={index} className="highlight">{part}</mark> : part
    );
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Retrieval Strategies</h1>
        <p className="page-description">
          Query your chunked documents using different retrieval strategies and compare their performance.
        </p>
      </div>

      {collections.length > 0 && (
        <div className="info-banner">
          <strong>Available:</strong> {collections.length} collection(s)
          <span style={{ color: 'var(--color-primary-400)' }}>|</span>
          <strong>Total Chunks:</strong> {collections.reduce((sum, col) => sum + col.chunks_count, 0)}
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <div className="grid-2">
        {/* Left Column: Query Configuration */}
        <div>
          <div className="card">
            <div className="card-header">
              <span className="card-icon">1</span>
              Enter Query
            </div>

            <div className="form-group">
              <label className="form-label">Your Question</label>
              <textarea
                className="input query-input"
                placeholder="What would you like to know about your documents?"
                value={lastQuery}
                onChange={(e) => setLastQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                rows="4"
              />
              <span className="hint-text">Press Enter to search, Shift+Enter for new line</span>
            </div>

            <div className="form-group">
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
              <span className="hint-text">Leave empty to search across all documents</span>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-icon">2</span>
              Retrieval Strategy
            </div>

            <div className="form-group">
              <label className="form-label">Strategy</label>
              <select
                className="select"
                value={selectedStrategy}
                onChange={(e) => setSelectedStrategy(e.target.value)}
              >
                {strategies.map(strategy => (
                  <option key={strategy.value} value={strategy.value}>
                    {strategy.label}
                  </option>
                ))}
              </select>
              {currentStrategy && (
                <p className="strategy-description">{currentStrategy.description}</p>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">
                Number of Results
                <span className="slider-value" style={{
                  display: 'inline-block',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 'var(--font-semibold)',
                  color: 'var(--color-primary-600)',
                  background: 'var(--color-primary-50)',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-primary-100)',
                  marginLeft: '8px'
                }}>{topK}</span>
              </label>
              <input
                type="range"
                min="1"
                max="20"
                step="1"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                className="slider"
              />
            </div>

            <button
              className="button"
              onClick={handleRetrieve}
              disabled={loading || !lastQuery.trim()}
              style={{ width: '100%' }}
            >
              {loading ? 'Searching...' : 'Retrieve Results'}
            </button>
          </div>

          {retrievalMetrics && (
            <MetricsDisplay metrics={retrievalMetrics} type="retrieval" />
          )}
        </div>

        {/* Right Column: Results */}
        <div>
          {retrievalResults.length > 0 && (
            <div className="card">
              <div className="card-header">
                <span className="card-icon" style={{ fontSize: 'var(--text-xs)' }}>&#128269;</span>
                Retrieved Results ({retrievalResults.length})
              </div>

              <div className="results-container">
                {retrievalResults.map((result, index) => (
                  <div key={index} className="result-item">
                    <div className="result-header">
                      <span className="result-rank">#{index + 1}</span>
                      <span className="result-score">
                        {result.score.toFixed(4)}
                      </span>
                      {(result.chunk_index !== undefined || result.metadata?.chunk_index !== undefined) && (
                        <span className="chunk-index-badge">
                          Index: {result.chunk_index ?? result.metadata?.chunk_index}
                        </span>
                      )}
                    </div>
                    <div className="result-text">
                      {highlightQuery(result.text, lastQuery)}
                    </div>
                    {result.document_id && (
                      <div className="result-doc-info">
                        Doc: {result.document_id}
                      </div>
                    )}
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <div className="result-metadata">
                        {Object.entries(result.metadata)
                          .filter(([key]) => key !== 'chunk_index')
                          .map(([key, value]) => (
                            <span key={key} className="metadata-tag">
                              {key}: {JSON.stringify(value)}
                            </span>
                          ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && retrievalResults.length === 0 && (
            <div className="card">
              <div className="no-results">
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem', opacity: 0.5 }}>&#128270;</div>
                <p>Enter a query to search</p>
                <p className="hint-text">Make sure you have chunked some documents first</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RetrievalStrategies;
