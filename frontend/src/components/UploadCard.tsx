import React, { useState, useRef } from 'react';
import { UploadIcon, FileTextIcon, CheckCircleIcon, AlertCircleIcon, TrashIcon, SpinnerIcon } from './Icons';
import { DocumentUploadResponse } from '../types';

interface UploadCardProps {
  currentDoc: string | null;
  pageCount: number;
  chunkCount: number;
  onUploadSuccess: (data: DocumentUploadResponse) => void;
  onDocumentRemoved: () => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({
  currentDoc,
  pageCount,
  chunkCount,
  onUploadSuccess,
  onDocumentRemoved,
}) => {
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF documents are supported.');
      return;
    }
    setError(null);
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }

      const data: DocumentUploadResponse = await res.json();
      onUploadSuccess(data);
    } catch (err: any) {
      setError(err.message || 'Error uploading document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (deleting || !currentDoc) return;
    setDeleting(true);
    setError(null);

    try {
      const res = await fetch('/api/document', {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to remove document');
      }

      onDocumentRemoved();
    } catch (err: any) {
      setError(err.message || 'Error removing document');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Document Ingestion</h2>
      <p className="card-desc">
        Upload a PDF document to extract page-indexed text, compute dense embeddings, and populate the in-memory vector index.
      </p>

      <div
        className="dropzone"
        onClick={() => {
          if (!uploading) fileInputRef.current?.click();
        }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!uploading && e.dataTransfer.files?.[0]) {
            handleFile(e.dataTransfer.files[0]);
          }
        }}
        style={{ cursor: uploading ? 'default' : 'pointer', opacity: uploading ? 0.85 : 1 }}
      >
        <input
          type="file"
          ref={fileInputRef}
          accept="application/pdf"
          style={{ display: 'none' }}
          disabled={uploading}
          onChange={(e) => {
            if (e.target.files?.[0]) {
              handleFile(e.target.files[0]);
            }
          }}
        />

        <div className="dropzone-content">
          <div className="dropzone-icon">
            {uploading ? <SpinnerIcon size={24} /> : <UploadIcon size={24} />}
          </div>
          <div style={{ width: '100%' }}>
            <div className="dropzone-label">
              {uploading ? 'Processing & embedding document...' : 'Click to upload or drag and drop PDF'}
            </div>
            <div className="dropzone-hint">
              {uploading
                ? 'Extracting text pages, generating dense vector embeddings, and indexing chunks...'
                : 'PDF files up to 20MB. Page numbers and metadata are extracted automatically.'}
            </div>
            {uploading && <div className="loader-bar" />}
          </div>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontSize: '13px' }}>
          <AlertCircleIcon size={16} />
          <span>{error}</span>
        </div>
      )}

      {currentDoc && (
        <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileTextIcon size={18} className="dropzone-icon" />
            <div>
              <div style={{ fontWeight: 500, fontSize: '13px', color: 'var(--text-primary)' }}>{currentDoc}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{pageCount} Pages · {chunkCount} Chunks Indexed</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="badge badge-green">
              <CheckCircleIcon size={12} />
              Active
            </span>
            <button
              type="button"
              className="btn-danger-outline"
              onClick={(e) => {
                e.stopPropagation();
                handleDelete();
              }}
              disabled={deleting}
              title="Remove uploaded document"
            >
              {deleting ? (
                <>
                  <SpinnerIcon size={13} />
                  <span>Removing...</span>
                </>
              ) : (
                <>
                  <TrashIcon size={13} />
                  <span>Delete</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
