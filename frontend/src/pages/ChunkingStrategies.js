import React, { useState } from 'react';
import { api } from '../api';
import DocumentUploader from '../components/DocumentUploader';
import DocumentViewer from '../components/DocumentViewer';
import ChunkViewer from '../components/ChunkViewer';
import MetricsDisplay from '../components/MetricsDisplay';
import './ChunkingStrategies.css';

const ChunkingStrategies = () => {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentContent, setDocumentContent] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('semantic');
  const [chunkSize, setChunkSize] = useState(512);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chunkingMetrics, setChunkingMetrics] = useState(null);

  const strategies = [
    { value: 'semantic', label: 'Semantic Chunking', description: 'Groups text based on semantic similarity between sentences' },
    { value: 'agentic_proposition', label: 'Agentic Proposition', description: 'Extracts atomic propositions using LLM' },
    { value: 'hybrid', label: 'Hybrid Chunking', description: 'Combines structural and character-based splitting' }
  ];

  const handleDocumentUploaded = async (docData) => {
    setSelectedDocument(docData);
    setError('');

    try {
      const fullDoc = await api.getDocument(docData.document_id);
      setDocumentContent(fullDoc.content);
    } catch (err) {
      setError('Failed to load document content');
    }
  };

  const handleChunk = async () => {
    if (!selectedDocument) {
      setError('Please upload a document first');
      return;
    }

    setLoading(true);
    setError('');
    setChunks([]);

    try {
      const result = await api.chunkDocument(
        selectedDocument.document_id,
        selectedStrategy,
        chunkSize,
        chunkOverlap
      );

      setChunks(result.chunks);
      setChunkingMetrics({
        strategy: selectedStrategy,
        latency: result.latency_ms,
        totalChunks: result.total_chunks
      });
    } catch (err) {
      setError(err.message || 'Chunking failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Chunking Strategies</h1>
        <p className="page-description">
          Upload a document and test different chunking strategies to see how they split your content.
        </p>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="grid-2">
        {/* Left Column: Upload and Configuration */}
        <div>
          <div className="card">
            <div className="card-header">
              <span className="card-icon">1</span>
              Upload Document
            </div>
            <DocumentUploader onUpload={handleDocumentUploaded} />

            {selectedDocument && (
              <div className="document-info">
                <span className="metrics-badge">
                  {selectedDocument.filename}
                </span>
                <span className="metrics-badge">
                  {selectedDocument.text_length?.toLocaleString()} characters
                </span>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-icon">2</span>
              Configure Strategy
            </div>

            <div className="form-group">
              <label className="form-label">Strategy</label>
              <div className="strategy-cards">
                {strategies.map(strategy => (
                  <div
                    key={strategy.value}
                    className={`strategy-card ${selectedStrategy === strategy.value ? 'selected' : ''}`}
                    onClick={() => setSelectedStrategy(strategy.value)}
                  >
                    <div className="strategy-card-title">{strategy.label}</div>
                    <div className="strategy-card-desc">{strategy.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Chunk Size
                <span className="slider-value">{chunkSize} chars</span>
              </label>
              <input
                type="range"
                min="128"
                max="2048"
                step="128"
                value={chunkSize}
                onChange={(e) => setChunkSize(parseInt(e.target.value))}
                className="slider"
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Chunk Overlap
                <span className="slider-value">{chunkOverlap} chars</span>
              </label>
              <input
                type="range"
                min="0"
                max="200"
                step="10"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
                className="slider"
              />
            </div>

            <button
              className="button"
              onClick={handleChunk}
              disabled={loading || !selectedDocument}
              style={{ width: '100%' }}
            >
              {loading ? 'Processing...' : 'Generate Chunks'}
            </button>
          </div>

          {chunkingMetrics && (
            <MetricsDisplay metrics={chunkingMetrics} type="chunking" />
          )}
        </div>

        {/* Right Column: Document and Chunks View */}
        <div>
          {documentContent && (
            <DocumentViewer
              content={documentContent}
              filename={selectedDocument?.filename}
            />
          )}

          {chunks.length > 0 && (
            <ChunkViewer chunks={chunks} />
          )}

          {!documentContent && chunks.length === 0 && (
            <div className="card">
              <div style={{ textAlign: 'center', padding: 'var(--space-12) var(--space-6)', color: 'var(--color-neutral-400)' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem', opacity: 0.5 }}>&#128196;</div>
                <p style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-medium)', marginBottom: '0.5rem', color: 'var(--color-neutral-500)' }}>No document uploaded yet</p>
                <p style={{ fontSize: 'var(--text-sm)' }}>Upload a document to get started with chunking</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChunkingStrategies;
