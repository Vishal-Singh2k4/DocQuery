import os
import io
import time
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.rag_engine import RAGEngine
from backend.schemas import (
    QueryRequest, 
    QueryResponse, 
    DocumentUploadResponse, 
    DeleteDocumentResponse,
    HealthResponse, 
    EvalSummary,
    SourceCitation
)
from backend.evaluate import run_evaluation

# Initialize FastAPI app
app = FastAPI(
    title="DocQuery API",
    description="Grounded PDF Question-Answering Service with Citations, Guardrails, and Evaluation",
    version="1.0.0"
)

# Enable CORS for frontend clients (Netlify & local Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = RAGEngine()

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    active_doc = list(rag_engine.documents.keys())[0] if rag_engine.documents else None
    total_pages = rag_engine.documents.get(active_doc, 0) if active_doc else 0
    return HealthResponse(
        status="healthy",
        documents_loaded=len(rag_engine.documents),
        total_chunks=len(rag_engine.chunks),
        active_document=active_doc,
        total_pages=total_pages
    )

@app.get("/")
def root():
    return {
        "name": "DocQuery API",
        "status": "online",
        "health": "/api/health",
        "docs": "/docs"
    }

@app.delete("/api/document", response_model=DeleteDocumentResponse)
def delete_document(filename: Optional[str] = None):
    if filename:
        rag_engine.remove_document(filename)
        msg = f"Document '{filename}' removed."
    else:
        rag_engine.clear_documents()
        msg = "All uploaded documents removed."
    return DeleteDocumentResponse(
        status="success",
        message=msg,
        documents_remaining=len(rag_engine.documents)
    )

@app.delete("/api/document/{filename}", response_model=DeleteDocumentResponse)
def delete_specific_document(filename: str):
    rag_engine.remove_document(filename)
    return DeleteDocumentResponse(
        status="success",
        message=f"Document '{filename}' removed.",
        documents_remaining=len(rag_engine.documents)
    )

@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts and parses an uploaded PDF document.
    Extracts text page-by-page, generates embeddings, and indexes chunks.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")

    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        res = rag_engine.ingest_pdf(file_bytes, file.filename)
        if res.get("status") == "error":
            raise HTTPException(status_code=422, detail=res.get("message", "Failed to process PDF."))

        return DocumentUploadResponse(
            filename=res["filename"],
            total_pages=res["total_pages"],
            total_chunks=res["total_chunks"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """
    Answers a question grounded strictly in indexed document evidence.
    Applies guardrails against hallucinations and returns exact page citations.
    """
    if not rag_engine.chunks:
        raise HTTPException(status_code=400, detail="No documents indexed. Please upload a PDF first.")

    res = rag_engine.query(request.question, top_k=request.top_k)
    citations = [SourceCitation(**s) for s in res.get("sources", [])]

    return QueryResponse(
        answer=res["answer"],
        sources=citations,
        has_sufficient_context=res["has_sufficient_context"],
        confidence=res["confidence"]
    )

@app.post("/api/evaluate", response_model=EvalSummary)
def evaluate_system():
    try:
        summary = run_evaluation()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("backend.server:app", host=host, port=port, reload=True)
