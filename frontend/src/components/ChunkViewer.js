import React, { useState } from 'react';
import './ChunkViewer.css';

const ChunkViewer = ({ chunks }) => {
  const [expandedChunks, setExpandedChunks] = useState(new Set());

  const toggleChunk = (chunkId) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId);
    } else {
      newExpanded.add(chunkId);
    }
    setExpandedChunks(newExpanded);
  };

  return (
    <div className="card">
      <div className="card-header">
        📦 Generated Chunks ({chunks.length})
      </div>
      
      <div className="chunks-container">
        {chunks.map((chunk, index) => {
          const isExpanded = expandedChunks.has(chunk.id);
          const shouldTruncate = chunk.text.length > 200;
          const displayText = isExpanded || !shouldTruncate 
            ? chunk.text 
            : chunk.text.substring(0, 200) + '...';

          return (
            <div key={chunk.id} className="chunk-item">
              <div className="chunk-header">
                <span className="chunk-number">Chunk #{index + 1}</span>
                <div className="chunk-stats">
                  {chunk.chunk_index !== undefined && (
                    <span className="chunk-index-badge">
                      Index: {chunk.chunk_index}
                    </span>
                  )}
                  <span className="stat-badge">
                    {chunk.char_count} chars
                  </span>
                  <span className="stat-badge">
                    {chunk.word_count} words
                  </span>
                </div>
              </div>
              
              <div className="chunk-text">{displayText}</div>
              
              {shouldTruncate && (
                <button
                  className="expand-button"
                  onClick={() => toggleChunk(chunk.id)}
                >
                  {isExpanded ? 'Show Less' : 'Show More'}
                </button>
              )}
              
              {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
                <div className="chunk-metadata">
                  {Object.entries(chunk.metadata).map(([key, value]) => (
                    <span key={key} className="metadata-item">
                      <strong>{key}:</strong> {JSON.stringify(value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ChunkViewer;
