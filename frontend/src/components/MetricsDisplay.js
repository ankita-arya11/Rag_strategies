import React from 'react';
import './MetricsDisplay.css';

const MetricsDisplay = ({ metrics, type }) => {
  const getMetricColor = (latency) => {
    if (latency < 1000) return '#4CAF50'; // Green
    if (latency < 3000) return '#FF9800'; // Orange
    return '#f44336'; // Red
  };

  const latencyColor = getMetricColor(metrics.latency);

  return (
    <div className="card">
      <div className="card-header">⚡ Performance Metrics</div>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Strategy</div>
          <div className="metric-value strategy-value">
            {metrics.strategy}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Latency</div>
          <div 
            className="metric-value latency-value"
            style={{ color: latencyColor }}
          >
            {metrics.latency.toFixed(2)} ms
          </div>
        </div>

        {type === 'chunking' && metrics.totalChunks !== undefined && (
          <div className="metric-card">
            <div className="metric-label">Total Chunks</div>
            <div className="metric-value">
              {metrics.totalChunks}
            </div>
          </div>
        )}

        {type === 'retrieval' && metrics.totalResults !== undefined && (
          <div className="metric-card">
            <div className="metric-label">Results Found</div>
            <div className="metric-value">
              {metrics.totalResults}
            </div>
          </div>
        )}
      </div>

      <div className="performance-indicator">
        <div className="indicator-label">Performance:</div>
        <div className="indicator-bar">
          <div 
            className="indicator-fill"
            style={{
              width: `${Math.min(100, (3000 - Math.min(metrics.latency, 3000)) / 3000 * 100)}%`,
              backgroundColor: latencyColor
            }}
          ></div>
        </div>
        <div className="indicator-text">
          {metrics.latency < 1000 ? 'Excellent' : 
           metrics.latency < 2000 ? 'Good' :
           metrics.latency < 3000 ? 'Fair' : 'Slow'}
        </div>
      </div>
    </div>
  );
};

export default MetricsDisplay;
