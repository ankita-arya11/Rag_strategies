import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import './App.css';
import ChunkingStrategies from './pages/ChunkingStrategies';
import RetrievalStrategies from './pages/RetrievalStrategies';
import ResultComparison from './components/ResultComparison';
import CollectionsViewer from './pages/CollectionsViewer';
import { AppProvider } from './context/AppContext';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="App">
          <nav className="navbar">
            <div className="nav-container">
              <div className="nav-brand">
                <div className="nav-logo">R</div>
                <div>
                  <div className="nav-title">RAG Strategies</div>
                </div>
              </div>
              <div className="nav-links">
                <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Chunking
                </NavLink>
                <NavLink to="/retrieval" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Retrieval
                </NavLink>
                <NavLink to="/compare" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Compare
                </NavLink>
                <NavLink to="/collections" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Collections
                </NavLink>
              </div>
            </div>
          </nav>

          <Routes>
            <Route path="/" element={<ChunkingStrategies />} />
            <Route path="/retrieval" element={<RetrievalStrategies />} />
            <Route path="/compare" element={<ResultComparison />} />
            <Route path="/collections" element={<CollectionsViewer />} />
          </Routes>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
