import React, { useState } from 'react';
import { PlayIcon, CheckCircleIcon, XCircleIcon, AlertCircleIcon, SpinnerIcon } from './Icons';
import { EvalSummary, EvalResultItem } from '../types';

export const BenchmarkPanel: React.FC = () => {
  const [evaluating, setEvaluating] = useState(false);
  const [summary, setSummary] = useState<EvalSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runBenchmark = async () => {
    setError(null);
    setEvaluating(true);

    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Evaluation benchmark failed');
      }

      const data: EvalSummary = await res.json();
      setSummary(data);
    } catch (err: any) {
      setError(err.message || 'Error running evaluation benchmark');
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <h2 className="card-title">10-Question Evaluation Benchmark</h2>
          <p className="card-desc" style={{ marginBottom: 0 }}>
            Automated test benchmark evaluating factual grounding, source attribution, and anti-hallucination guardrail rejection.
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={runBenchmark}
          disabled={evaluating}
        >
          {evaluating ? (
            <>
              <SpinnerIcon size={14} />
              <span>Running Benchmark...</span>
            </>
          ) : (
            <>
              <PlayIcon size={16} />
              <span>Run Benchmark</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontSize: '13px', marginBottom: '16px' }}>
          <AlertCircleIcon size={16} />
          <span>{error}</span>
        </div>
      )}

      {evaluating && (
        <div style={{ marginTop: '16px', marginBottom: '20px', padding: '16px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <SpinnerIcon size={18} />
            <div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>
                Executing Evaluation Suite (10 Questions)
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Testing factual precision, page citation attribution, and negative guardrail refusal...
              </div>
            </div>
          </div>
          <div className="loader-bar" style={{ marginTop: '12px' }} />
        </div>
      )}

      {summary && (
        <>
          {/* Stat Grid */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-value">{summary.total}</div>
              <div className="stat-label">Total Questions</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#34d399' }}>{summary.correct}</div>
              <div className="stat-label">Correct Answers</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#60a5fa' }}>{summary.accuracy_percent}%</div>
              <div className="stat-label">Accuracy Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#fbbf24' }}>{summary.unsupported_rejected} / 1</div>
              <div className="stat-label">Guardrail Refusals</div>
            </div>
          </div>

          {/* Results Table */}
          <div style={{ overflowX: 'auto', border: '1px solid var(--border-color)', borderRadius: 'var(--radius)' }}>
            <table className="benchmark-table">
              <thead>
                <tr>
                  <th style={{ width: '45px' }}>ID</th>
                  <th>Test Question</th>
                  <th>Expected Ground Truth</th>
                  <th>Model Answer</th>
                  <th style={{ width: '90px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {summary.results.map((item: EvalResultItem) => (
                  <tr key={item.question_id}>
                    <td style={{ color: 'var(--text-muted)', fontWeight: 500 }}>
                      #{item.question_id}
                    </td>
                    <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                      {item.question}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {item.expected}
                    </td>
                    <td style={{ color: 'var(--text-primary)' }}>
                      {item.actual}
                    </td>
                    <td>
                      {item.is_correct ? (
                        <span className="badge badge-green">
                          <CheckCircleIcon size={12} />
                          Pass
                        </span>
                      ) : (
                        <span className="badge badge-red">
                          <XCircleIcon size={12} />
                          Fail
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!evaluating && !summary && (
        <div className="empty-state">
          <div className="empty-state-title">Benchmark ready to execute</div>
          <div className="empty-state-desc">
            Click "Run Benchmark" above to automatically execute all 10 ground-truth questions against the test document and view the live scorecard.
          </div>
        </div>
      )}
    </div>
  );
};
