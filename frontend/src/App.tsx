import React, { useState, useEffect } from 'react';
import { UploadCard } from './components/UploadCard';
import { ChatPanel } from './components/ChatPanel';
import { BenchmarkPanel } from './components/BenchmarkPanel';
import { ShieldCheckIcon, SpinnerIcon } from './components/Icons';
import { HealthResponse, DocumentUploadResponse } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'benchmark'>('chat');
  const [docName, setDocName] = useState<string | null>(null);
  const [pageCount, setPageCount] = useState<number>(0);
  const [chunkCount, setChunkCount] = useState<number>(0);
  const [serverOnline, setServerOnline] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data: HealthResponse) => {
        if (data.status === 'healthy') {
          setServerOnline(true);
          if (data.documents_loaded > 0 && data.active_document) {
            setDocName(data.active_document);
            setPageCount(data.total_pages || 0);
            setChunkCount(data.total_chunks);
          }
        }
      })
      .catch(() => setServerOnline(false));
  }, []);

  const handleUploadSuccess = (data: DocumentUploadResponse) => {
    setDocName(data.filename);
    setPageCount(data.total_pages);
    setChunkCount(data.total_chunks);
  };

  const handleDocumentRemoved = () => {
    setDocName(null);
    setPageCount(0);
    setChunkCount(0);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1 className="header-title">DocQuery</h1>
          <p className="header-subtitle">
            Grounded PDF Question-Answering system with page citations, anti-hallucination guardrails, and automated evaluation.
          </p>
        </div>
        <div className="header-meta">
          <span className={`badge ${serverOnline ? 'badge-green' : 'badge-amber'}`}>
            {serverOnline ? <ShieldCheckIcon size={12} /> : <SpinnerIcon size={12} />}
            {serverOnline ? 'Backend Online' : 'Connecting to API'}
          </span>
        </div>
      </header>

      {/* Upload Section */}
      <UploadCard
        currentDoc={docName}
        pageCount={pageCount}
        chunkCount={chunkCount}
        onUploadSuccess={handleUploadSuccess}
        onDocumentRemoved={handleDocumentRemoved}
      />

      {/* Tab Navigation */}
      <nav className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Document Q&A
        </button>
        <button
          className={`tab-btn ${activeTab === 'benchmark' ? 'active' : ''}`}
          onClick={() => setActiveTab('benchmark')}
        >
          Evaluation Benchmark (10 Questions)
        </button>
      </nav>

      {/* Tab Content */}
      <main>
        {activeTab === 'chat' ? (
          <ChatPanel hasDocument={Boolean(docName)} />
        ) : (
          <BenchmarkPanel />
        )}
      </main>
    </div>
  );
};

export default App;
