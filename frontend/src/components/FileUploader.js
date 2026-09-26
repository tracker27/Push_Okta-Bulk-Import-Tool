import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUploader.css';

function FileUploader({ onFileUpload, loading, flow }) {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
    },
    disabled: loading,
  });

  return (
    <div className="file-uploader">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${loading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <span className="upload-icon">📁</span>
          {isDragActive ? (
            <p>Drop the CSV file here...</p>
          ) : (
            <>
              <p className="main-text">Drag and drop your CSV file here</p>
              <p className="sub-text">or click to select a file</p>
            </>
          )}
        </div>
      </div>

      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Processing your file...</p>
        </div>
      )}

      <div className="template-info">
        <h4>📋 Template Information</h4>
        {flow === 'new-users' ? (
          <p>
            Required columns: <code>login</code>, <code>firstName</code>, <code>lastName</code>, <code>email</code>
            <br />
            Optional columns: middleName, title, phone, department, etc.
          </p>
        ) : (
          <p>
            Required column: <code>userIdOrLogin</code> (user email)
          </p>
        )}
      </div>
    </div>
  );
}

export default FileUploader;
