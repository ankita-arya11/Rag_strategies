import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // Load initial state from sessionStorage
  const loadFromSession = (key, defaultValue) => {
    try {
      const saved = sessionStorage.getItem(key);
      return saved ? JSON.parse(saved) : defaultValue;
    } catch {
      return defaultValue;
    }
  };

  // Documents
  const [documents, setDocuments] = useState([]);
  
  // Chunking results
  const [chunkingResults, setChunkingResults] = useState(
    loadFromSession('chunkingResults', {})
  );
  
  // Retrieval results
  const [retrievalResults, setRetrievalResults] = useState(
    loadFromSession('retrievalResults', {})
  );
  
  // Comparison results
  const [comparisonResults, setComparisonResults] = useState(
    loadFromSession('comparisonResults', {})
  );
  
  // Last query
  const [lastQuery, setLastQuery] = useState(
    loadFromSession('lastQuery', '')
  );
  
  // Selected document
  const [selectedDocument, setSelectedDocument] = useState(
    loadFromSession('selectedDocument', '')
  );

  // Collections
  const [collections, setCollections] = useState([]);

  // Persist to sessionStorage on changes
  useEffect(() => {
    sessionStorage.setItem('chunkingResults', JSON.stringify(chunkingResults));
  }, [chunkingResults]);

  useEffect(() => {
    sessionStorage.setItem('retrievalResults', JSON.stringify(retrievalResults));
  }, [retrievalResults]);

  useEffect(() => {
    sessionStorage.setItem('comparisonResults', JSON.stringify(comparisonResults));
  }, [comparisonResults]);

  useEffect(() => {
    sessionStorage.setItem('lastQuery', JSON.stringify(lastQuery));
  }, [lastQuery]);

  useEffect(() => {
    sessionStorage.setItem('selectedDocument', JSON.stringify(selectedDocument));
  }, [selectedDocument]);

  // Clear all session data
  const clearSession = () => {
    setChunkingResults({});
    setRetrievalResults({});
    setComparisonResults({});
    setLastQuery('');
    setSelectedDocument('');
    sessionStorage.clear();
  };

  const value = {
    // Documents
    documents,
    setDocuments,
    
    // Chunking
    chunkingResults,
    setChunkingResults,
    
    // Retrieval
    retrievalResults,
    setRetrievalResults,
    
    // Comparison
    comparisonResults,
    setComparisonResults,
    
    // Query & Document
    lastQuery,
    setLastQuery,
    selectedDocument,
    setSelectedDocument,
    
    // Collections
    collections,
    setCollections,
    
    // Utilities
    clearSession,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
