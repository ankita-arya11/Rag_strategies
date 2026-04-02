const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export const api = {
  // Document operations
  uploadDocument: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Create an abort controller for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
    
    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || 'Upload failed');
      }
      
      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Upload timeout - file may be too large');
      }
      throw error;
    }
  },

  getDocuments: async () => {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
      throw new Error('Failed to fetch documents');
    }
    return response.json();
  },

  getDocument: async (documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch document');
    }
    return response.json();
  },

  // Chunking operations
  chunkDocument: async (documentId, strategy, chunkSize = 512, chunkOverlap = 50) => {
    const response = await fetch(`${API_BASE_URL}/chunk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: documentId,
        strategy,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Chunking failed');
    }
    
    return response.json();
  },

  // Retrieval operations
  retrieve: async (query, strategy, documentId = null, topK = 5) => {
    const response = await fetch(`${API_BASE_URL}/retrieve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        strategy,
        document_id: documentId,
        top_k: topK,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Retrieval failed');
    }
    
    return response.json();
  },

  // Metrics
  getMetrics: async () => {
    const response = await fetch(`${API_BASE_URL}/metrics`);
    if (!response.ok) {
      throw new Error('Failed to fetch metrics');
    }
    return response.json();
  },

  getMetricsComparison: async () => {
    const response = await fetch(`${API_BASE_URL}/metrics/compare`);
    if (!response.ok) {
      throw new Error('Failed to fetch metrics comparison');
    }
    return response.json();
  },

  // Collections
  getCollections: async () => {
    const response = await fetch(`${API_BASE_URL}/collections`);
    if (!response.ok) {
      throw new Error('Failed to fetch collections');
    }
    return response.json();
  },

  getCollectionChunks: async (collectionName) => {
    const response = await fetch(`${API_BASE_URL}/collections/${collectionName}/chunks`);
    if (!response.ok) {
      throw new Error('Failed to fetch collection chunks');
    }
    return response.json();
  },

  // Strategies
  getStrategies: async () => {
    const response = await fetch(`${API_BASE_URL}/strategies`);
    if (!response.ok) {
      throw new Error('Failed to fetch strategies');
    }
    return response.json();
  },

  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  },
};
