from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str = Field(..., description="The user question to ask about uploaded documents")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")

class SourceCitation(BaseModel):
    document_name: str = Field(..., description="Name of the source document")
    page_number: int = Field(..., description="1-indexed physical page number")
    text_snippet: str = Field(..., description="Extracted relevant text excerpt")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Evidence-grounded synthesized answer or explicit refusal")
    sources: List[SourceCitation] = Field(default_factory=list, description="List of source citations")
    has_sufficient_context: bool = Field(..., description="True if evidence was found, False if guardrail refused")
    confidence: str = Field(..., description="Confidence rating: High, Medium, or Insufficient Evidence")

class DocumentUploadResponse(BaseModel):
    filename: str
    total_pages: int
    total_chunks: int
    status: str

class DeleteDocumentResponse(BaseModel):
    status: str
    message: str
    documents_remaining: int

class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    total_chunks: int
    active_document: Optional[str] = None
    total_pages: Optional[int] = None

class EvalResultItem(BaseModel):
    question_id: int
    question: str
    expected: str
    actual: str
    is_correct: bool
    refusal_triggered: bool
    sources: List[SourceCitation] = Field(default_factory=list)

class EvalSummary(BaseModel):
    total: int
    correct: int
    accuracy_percent: float
    unsupported_rejected: int
    results: List[EvalResultItem]
