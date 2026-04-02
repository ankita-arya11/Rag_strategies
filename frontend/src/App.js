import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import './App.css';
import ChunkingStrategies from './pages/ChunkingStrategies';
import RetrievalStrategies from './pages/RetrievalStrategies';
import ResultComparison from './components/ResultComparison';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <div className="nav-brand">
              <div className="nav-logo">R</div>
              <div>
                <div className="nav-title">RAG Strategies</div>
                <div className="nav-title-sub">Testing Platform</div>
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
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<ChunkingStrategies />} />
          <Route path="/retrieval" element={<RetrievalStrategies />} />
          <Route path="/compare" element={<ResultComparison />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
