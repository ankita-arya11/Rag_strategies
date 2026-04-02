import React, { useState } from 'react';
import { api } from '../api';
import './DocumentUploader.css';

const DocumentUploader = ({ onUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState('');

  const handleFileSelect = async (file) => {
    if (!file) return;

    // Validate file type
    const validTypes = ['.pdf', '.txt', '.docx', '.doc'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(fileExtension)) {
      setError(`Invalid file type. Supported: ${validTypes.join(', ')}`);
      return;
    }

    // Validate file size (max 50MB to match backend)
    if (file.size > 50 * 1024 * 1024) {
      setError('File too large. Maximum size is 50MB');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const result = await api.uploadDocument(file);
      setError(''); // Clear any previous errors
      onUpload(result);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  return (
    <div className="uploader-container">
      <div
        className={`upload-area ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          id="file-input"
          className="file-input"
          onChange={handleFileInput}
          accept=".pdf,.txt,.docx,.doc"
          disabled={uploading}
        />
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-icon">📁</div>
          <div className="upload-text">
            {uploading ? 'Uploading...' : 'Click or drag file to upload'}
          </div>
          <div className="upload-hint">
            Supported: PDF, TXT, DOCX (max 10MB)
          </div>
        </label>
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
};

export default DocumentUploader;
