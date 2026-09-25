export interface SourceCitation {
  document_name: string;
  page_number: number;
  text_snippet: string;
  similarity_score: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceCitation[];
  has_sufficient_context: boolean;
  confidence: 'High' | 'Medium' | 'Insufficient Evidence' | 'Error';
}

export interface DocumentUploadResponse {
  filename: string;
  total_pages: number;
  total_chunks: number;
  status: string;
}

export interface DeleteDocumentResponse {
  status: string;
  message: string;
  documents_remaining: number;
}

export interface HealthResponse {
  status: string;
  documents_loaded: number;
  total_chunks: number;
  active_document?: string;
  total_pages?: number;
}

export interface EvalResultItem {
  question_id: number;
  question: string;
  expected: string;
  actual: string;
  is_correct: boolean;
  refusal_triggered: boolean;
  sources: SourceCitation[];
}

export interface EvalSummary {
  total: number;
  correct: number;
  accuracy_percent: number;
  unsupported_rejected: number;
  results: EvalResultItem[];
}
