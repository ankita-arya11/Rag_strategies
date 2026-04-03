import React, { useState } from 'react';
import './ChunkViewer.css';

const ChunkViewer = ({ chunks }) => {
  const [expandedChunks, setExpandedChunks] = useState({});

  const toggleChunk = (chunkId) => {
    setExpandedChunks(prev => ({
      ...prev,
      [chunkId]: !prev[chunkId]
    }));
  };

  return (
    <div className="card">
      <div className="card-header">
        📦 Generated Chunks ({chunks.length})
      </div>
      
      <div className="chunks-container">
        {chunks.map((chunk, index) => {
          const isExpanded = expandedChunks[index];
          const shouldTruncate = chunk.text.length > 200;
          const displayText = !shouldTruncate || isExpanded
            ? chunk.text 
            : chunk.text.substring(0, 200) + '...';

          return (
            <div key={index} className="chunk-item">
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
              
              <div className={`chunk-text ${isExpanded ? 'expanded' : ''}`}>
                {displayText}
              </div>
              
              {shouldTruncate && (
                <button
                  className="expand-button"
                  onClick={() => toggleChunk(index)}
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
