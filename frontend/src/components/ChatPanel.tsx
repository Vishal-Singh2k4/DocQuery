import React, { useState } from 'react';
import { SendIcon, ShieldCheckIcon, AlertCircleIcon, FileTextIcon, SpinnerIcon } from './Icons';
import { QueryResponse } from '../types';

interface ChatPanelProps {
  hasDocument: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ hasDocument }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleQuestions = [
    'What programming languages are required?',
    'What LLM concepts should applicants understand?',
    'What are the internship working hours?',
    'What is the company annual revenue?',
  ];

  const handleQuery = async (queryText: string) => {
    if (!queryText.trim() || loading || !hasDocument) return;
    setError(null);
    setLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText, top_k: 3 }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Query request failed');
      }

      const data: QueryResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message || 'Error communicating with RAG server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Grounded Question Answering</h2>
      <p className="card-desc">
        Ask questions about the uploaded document. The RAG engine retrieves relevant chunks, isolates context, and prevents hallucination.
      </p>

      {/* Suggested Questions */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
          Suggested Test Queries:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              className="btn-secondary"
              style={{ fontSize: '12px', padding: '6px 12px' }}
              onClick={() => {
                setQuestion(q);
                handleQuery(q);
              }}
              disabled={loading || !hasDocument}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Query Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleQuery(question);
        }}
        className="query-box"
      >
        <input
          type="text"
          className="query-input"
          placeholder={hasDocument ? "Ask a factual question about the document..." : "Please upload a document above to enable queries..."}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading || !hasDocument}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !hasDocument || !question.trim()}
        >
          {loading ? (
            <>
              <SpinnerIcon size={14} />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <SendIcon size={16} />
              <span>Ask</span>
            </>
          )}
        </button>
      </form>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontSize: '13px', marginTop: '12px' }}>
          <AlertCircleIcon size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Answer Loading View */}
      {loading && (
        <div className="answer-container" style={{ borderColor: 'var(--border-focus)' }}>
          <div className="answer-header">
            <span className="answer-label">Synthesizing Answer</span>
            <span className="badge badge-blue">
              <SpinnerIcon size={12} />
              Retrieving Evidence
            </span>
          </div>
          <div style={{ padding: '8px 0 4px 0' }}>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Searching vector embeddings & verifying citations...
            </div>
            <div className="loader-bar" />
          </div>
        </div>
      )}

      {/* Answer View */}
      {!loading && response && (
        <div className="answer-container">
          <div className="answer-header">
            <span className="answer-label">Synthesized Evidence</span>
            {response.has_sufficient_context ? (
              <span className="badge badge-green">
                <ShieldCheckIcon size={12} />
                {response.confidence} Confidence
              </span>
            ) : (
              <span className="badge badge-amber">
                <AlertCircleIcon size={12} />
                Guardrail Triggered: Insufficient Context
              </span>
            )}
          </div>

          <div className="answer-text">
            {response.answer}
          </div>

          {/* Sources Section */}
          {response.sources.length > 0 && (
            <div className="citations-wrapper">
              <div className="citations-title">
                Granular Source Attribution ({response.sources.length} Chunks Retrieved)
              </div>
              <div className="citation-list">
                {response.sources.map((src, i) => (
                  <div key={i} className="citation-item">
                    <div className="citation-meta">
                      <span className="badge badge-blue">
                        <FileTextIcon size={11} />
                        Page {src.page_number}
                      </span>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {src.document_name}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                        Similarity: {Math.round(src.similarity_score * 100)}%
                      </span>
                    </div>
                    <div className="citation-snippet">
                      "{src.text_snippet}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty States */}
      {!loading && !response && (
        <div className="empty-state">
          <div className="empty-state-title">
            {hasDocument ? "No queries executed yet" : "No document active"}
          </div>
          <div className="empty-state-desc">
            {hasDocument
              ? "Type a question above or select one of the suggested queries to verify semantic search, hallucination guardrails, and page citations."
              : "Upload a PDF document above to start asking questions, inspect citations, and verify guardrail responses."}
          </div>
        </div>
      )}
    </div>
  );
};
