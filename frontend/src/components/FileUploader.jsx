import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, Image as ImageIcon, Table, X, CheckCircle, AlertCircle } from 'lucide-react';

export default function FileUploader({ selectedFile, onFileSelect, onClearFile, error }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const inputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileIcon = (file) => {
    if (!file) return <FileText size={24} />;
    const ext = file.name.split('.').pop().toLowerCase();
    if (['xlsx', 'xls', 'csv'].includes(ext)) {
      return <Table size={24} className="text-success" />;
    }
    if (['png', 'jpg', 'jpeg', 'tiff', 'webp', 'bmp'].includes(ext)) {
      return <ImageIcon size={24} className="text-info" />;
    }
    return <FileText size={24} className="text-primary" />;
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
    onFileSelect(file);
  };

  const handleClear = (e) => {
    e.stopPropagation();
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (inputRef.current) {
      inputRef.current.value = '';
    }
    onClearFile();
  };

  return (
    <div className="w-100">
      <input
        ref={inputRef}
        type="file"
        id="fileInput"
        className="d-none"
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif,.bmp,.webp,.xlsx,.xls,.csv"
        onChange={handleFileChange}
      />

      {!selectedFile ? (
        <div
          id="dropzoneContainer"
          className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current && inputRef.current.click()}
        >
          <div className="dropzone-icon-wrap">
            <UploadCloud size={34} />
          </div>
          
          <h5 className="fw-semibold mb-1" style={{ color: '#fff' }}>
            Drag and drop your document
          </h5>
          <p className="text-muted small mb-3">
            PDF, PNG, JPG, JPEG, TIFF, XLSX, CSV
          </p>

          <button 
            type="button" 
            className="btn btn-sm btn-outline-light px-3 py-2 rounded-pill fw-medium"
            style={{ borderColor: 'rgba(255, 255, 255, 0.25)', fontSize: '0.85rem' }}
          >
            Select a file from your device
          </button>
        </div>
      ) : (
        <div 
          className="p-3 rounded-3 d-flex align-items-center justify-content-between"
          style={{ 
            background: 'rgba(15, 20, 34, 0.9)', 
            border: '1px solid rgba(99, 102, 241, 0.4)',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
          }}
        >
          <div className="d-flex align-items-center gap-3">
            {previewUrl ? (
              <img 
                src={previewUrl} 
                alt="Thumbnail" 
                style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '8px', border: '1px solid var(--border-card)' }} 
              />
            ) : (
              <div 
                style={{
                  width: '48px', 
                  height: '48px', 
                  borderRadius: '8px', 
                  background: 'rgba(99, 102, 241, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {getFileIcon(selectedFile)}
              </div>
            )}

            <div>
              <div className="d-flex align-items-center gap-2">
                <span className="fw-semibold text-light text-truncate" style={{ maxWidth: '280px' }}>
                  {selectedFile.name}
                </span>
                <span className="badge badge-glass-emerald small">
                  Ready
                </span>
              </div>
              <span className="text-muted small">
                {formatFileSize(selectedFile.size)} <span className="mx-1">•</span> {selectedFile.name.split('.').pop().toUpperCase()} Document
              </span>
            </div>
          </div>

          <div className="d-flex align-items-center gap-2">
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary rounded-pill px-2 py-1"
              style={{ fontSize: '0.8rem' }}
              onClick={() => inputRef.current && inputRef.current.click()}
              title="Replace file"
            >
              Replace
            </button>
            <button
              type="button"
              className="btn btn-sm btn-outline-danger rounded-circle p-1"
              style={{ width: '32px', height: '32px' }}
              onClick={handleClear}
              title="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 rounded-3 d-flex align-items-center gap-2 text-danger small" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
          <AlertCircle size={18} className="flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
