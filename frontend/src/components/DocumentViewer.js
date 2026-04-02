import React, { useState } from 'react';
import './DocumentViewer.css';

const DocumentViewer = ({ content, filename }) => {
  const [expanded, setExpanded] = useState(false);

  const displayContent = expanded ? content : content.substring(0, 500);
  const hasMore = content.length > 500;

  return (
    <div className="card">
      <div className="card-header">
        📄 Document: {filename}
      </div>
      <div className="document-content">
        <pre className="document-text">{displayContent}</pre>
        {hasMore && !expanded && <div className="fade-overlay"></div>}
      </div>
      {hasMore && (
        <button 
          className="button button-secondary"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show Less' : 'Show More'}
        </button>
      )}
      <div className="document-stats">
        <span className="metrics-badge">
          Characters: {content.length.toLocaleString()}
        </span>
        <span className="metrics-badge">
          Words: {content.split(/\s+/).length.toLocaleString()}
        </span>
        <span className="metrics-badge">
          Lines: {content.split('\n').length.toLocaleString()}
        </span>
      </div>
    </div>
  );
};

export default DocumentViewer;
