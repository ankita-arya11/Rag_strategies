import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './CollectionsViewer.css';

const CollectionsViewer = () => {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    setLoading(true);
    try {
      const data = await api.getCollections();
      setCollections(data.collections || []);
    } catch (err) {
      setError('Failed to load collections');
    } finally {
      setLoading(false);
    }
  };

  const loadChunks = async (collectionName) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getCollectionChunks(collectionName);
      setChunks(data.chunks || []);
      setSelectedCollection(collectionName);
    } catch (err) {
      setError(`Failed to load chunks: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredChunks = chunks.filter(chunk =>
    chunk.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">📦 Collections & Chunks</h1>
        <p className="page-description">
          View all vector collections and their stored chunks
        </p>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="grid-2">
        {/* Left Column: Collections List */}
        <div>
          <div className="card">
            <div className="card-header">
              <span className="card-icon">📚</span>
              Collections ({collections.length})
            </div>

            {loading && !selectedCollection ? (
              <div style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
                <p>Loading collections...</p>
              </div>
            ) : collections.length === 0 ? (
              <div className="empty-state">
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📦</div>
                <p>No collections found</p>
                <p className="hint-text">Upload and chunk documents first</p>
              </div>
            ) : (
              <div className="collections-list">
                {collections.map((collection) => (
                  <div
                    key={collection.name}
                    className={`collection-item ${selectedCollection === collection.name ? 'active' : ''}`}
                    onClick={() => loadChunks(collection.name)}
                  >
                    <div className="collection-name">
                      <span className="collection-icon">🗂️</span>
                      {collection.name}
                    </div>
                    <div className="collection-meta">
                      <span className="chunks-count">
                        {collection.chunks_count} chunks
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            className="button"
            onClick={loadCollections}
            disabled={loading}
            style={{ width: '100%', marginTop: 'var(--space-4)' }}
          >
            🔄 Refresh Collections
          </button>
        </div>

        {/* Right Column: Chunks Viewer */}
        <div>
          {selectedCollection ? (
            <div className="card">
              <div className="card-header">
                <span className="card-icon">📄</span>
                Chunks in: {selectedCollection}
              </div>

              {/* Search box */}
              <div className="search-box">
                <input
                  type="text"
                  className="input"
                  placeholder="🔍 Search within chunks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {loading ? (
                <div style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
                  <p>Loading chunks...</p>
                </div>
              ) : filteredChunks.length === 0 ? (
                <div className="empty-state">
                  <p>
                    {searchTerm ? 'No chunks match your search' : 'No chunks found'}
                  </p>
                </div>
              ) : (
                <div className="chunks-container">
                  <div className="chunks-summary">
                    Showing {filteredChunks.length} of {chunks.length} chunks
                  </div>
                  {filteredChunks.map((chunk, index) => (
                    <div key={chunk.id || index} className="chunk-item">
                      <div className="chunk-header">
                        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
                          <span className="chunk-id">#{index + 1}</span>
                          {chunk.chunk_index !== undefined && (
                            <span className="chunk-index-badge">
                              Index: {chunk.chunk_index}
                            </span>
                          )}
                        </div>
                        <span className="chunk-doc-id">
                          Doc: {chunk.document_id?.substring(0, 8)}...
                        </span>
                      </div>
                      <div className="chunk-text">
                        {searchTerm ? (
                          highlightText(chunk.text, searchTerm)
                        ) : (
                          chunk.text
                        )}
                      </div>
                      {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
                        <div className="chunk-metadata">
                          <strong>Metadata:</strong>
                          <div className="metadata-grid">
                            {Object.entries(chunk.metadata).map(([key, value]) => (
                              <div key={key} className="metadata-item">
                                <span className="metadata-key">{key}:</span>
                                <span className="metadata-value">
                                  {JSON.stringify(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="card">
              <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
                <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>👈</div>
                <h3>Select a Collection</h3>
                <p className="hint-text">
                  Click on a collection from the left to view its chunks
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper function to highlight search term
const highlightText = (text, searchTerm) => {
  if (!searchTerm) return text;
  
  const parts = text.split(new RegExp(`(${searchTerm})`, 'gi'));
  return parts.map((part, index) =>
    part.toLowerCase() === searchTerm.toLowerCase() ? (
      <mark key={index} className="highlight">{part}</mark>
    ) : (
      part
    )
  );
};

export default CollectionsViewer;
