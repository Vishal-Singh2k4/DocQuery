import os
import re
import io
import time
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pypdf import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
backend_env = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

@dataclass
class DocumentChunk:
    chunk_id: str
    doc_name: str
    page_number: int
    text: str
    embedding: Optional[List[float]] = None

class RAGEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            
        self.chunks: List[DocumentChunk] = []
        self.documents: Dict[str, int] = {} # doc_name -> total_pages
        self.confidence_threshold: float = 0.40

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def clear_documents(self):
        """Clears all indexed documents and chunks from memory."""
        self.chunks.clear()
        self.documents.clear()

    def remove_document(self, filename: str):
        """Removes a specific document and its associated chunks."""
        self.chunks = [c for c in self.chunks if c.doc_name != filename]
        self.documents.pop(filename, None)

    def extract_text_from_pdf(self, file_bytes: bytes, filename: str) -> List[Tuple[int, str]]:
        """
        Extracts text from PDF bytes page by page.
        Returns a list of (page_number, text) tuples (1-indexed).
        """
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_content = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            # Clean excessive whitespaces while preserving readability
            cleaned_text = re.sub(r'[ \t]+', ' ', page_text).strip()
            if cleaned_text:
                pages_content.append((idx + 1, cleaned_text))
        
        self.documents[filename] = len(reader.pages)
        return pages_content

    def chunk_document(
        self, 
        pages_content: List[Tuple[int, str]], 
        filename: str, 
        chunk_size: int = 450, 
        chunk_overlap: int = 50
    ) -> List[DocumentChunk]:
        """
        Splits extracted pages into overlapping chunks while preserving page metadata.
        """
        new_chunks = []
        for page_num, text in pages_content:
            if len(text) <= chunk_size:
                chunk_id = f"{filename}_p{page_num}_c0"
                new_chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=filename,
                    page_number=page_num,
                    text=text
                ))
            else:
                start = 0
                c_idx = 0
                while start < len(text):
                    end = start + chunk_size
                    chunk_text = text[start:end].strip()
                    if chunk_text:
                        chunk_id = f"{filename}_p{page_num}_c{c_idx}"
                        new_chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            doc_name=filename,
                            page_number=page_num,
                            text=chunk_text
                        ))
                        c_idx += 1
                    start += (chunk_size - chunk_overlap)
        return new_chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense vector embeddings using Google Gemini gemini-embedding-001.
        """
        if not self.client:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in your environment.")

        # Batch embed (up to 100 items per call)
        batch_size = 50
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=batch,
            )
            # Response contains embeddings for each content
            for emb in response.embeddings:
                all_embeddings.append(emb.values)
        return all_embeddings

    def ingest_pdf(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Full ingestion pipeline: PDF -> Page Extraction -> Chunking -> Embeddings -> Storage.
        """
        pages = self.extract_text_from_pdf(file_bytes, filename)
        if not pages:
            return {"status": "error", "message": "No extractable text found in PDF"}

        chunks = self.chunk_document(pages, filename)
        texts = [c.text for c in chunks]
        
        embeddings = self.generate_embeddings(texts)
        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb
            
        self.chunks.extend(chunks)
        return {
            "status": "success",
            "filename": filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks)
        }

    def search(self, query: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """
        Encodes query, computes cosine similarity against all indexed chunks,
        and returns the top_k chunks with their similarity scores.
        """
        if not self.chunks:
            return []

        # Embed query
        query_emb_resp = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
        )
        query_vector = np.array(query_emb_resp.embeddings[0].values, dtype=np.float32)
        q_norm = np.linalg.norm(query_vector) + 1e-9

        scored_chunks = []
        for chunk in self.chunks:
            if chunk.embedding is not None:
                c_vec = np.array(chunk.embedding, dtype=np.float32)
                score = float(np.dot(query_vector, c_vec) / (q_norm * np.linalg.norm(c_vec) + 1e-9))
                scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Answers a user question strictly using retrieved evidence.
        Applies hallucination guardrail if evidence is insufficient.
        """
        top_results = self.search(question, top_k=top_k)
        
        if not top_results or top_results[0][1] < self.confidence_threshold:
            return {
                "answer": "I don't have enough information in the provided documents to answer this question.",
                "sources": [],
                "has_sufficient_context": False,
                "confidence": "Insufficient Evidence"
            }

        context_parts = []
        sources = []
        for chunk, score in top_results:
            context_parts.append(
                f'<document_chunk doc="{chunk.doc_name}" page="{chunk.page_number}">\n{chunk.text}\n</document_chunk>'
            )
            sources.append({
                "document_name": chunk.doc_name,
                "page_number": chunk.page_number,
                "text_snippet": chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
                "similarity_score": round(score, 4)
            })

        context_str = "\n\n".join(context_parts)

        system_instruction = (
            "You are a factual document question-answering assistant.\n"
            "Use only the facts provided inside the <document_context> tags.\n"
            "Do not infer, speculate, or draw from outside knowledge.\n"
            "If the context does not explicitly provide the answer, respond with:\n"
            "\"I don't have enough information in the provided documents to answer this question.\"\n"
            "Cite the relevant page numbers whenever information is referenced."
        )

        user_prompt = (
            f"<document_context>\n{context_str}\n</document_context>\n\n"
            f"User Question: {question}\n\n"
            "Answer:"
        )

        candidate_models = ["gemini-3.1-flash-lite", "gemini-3-flash-preview", "gemini-flash-latest"]
        raw_answer = ""
        last_error = None

        for model_name in candidate_models:
            for _ in range(2):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.0,
                        )
                    )
                    raw_answer = response.text.strip() if response.text else ""
                    if raw_answer:
                        break
                except Exception as e:
                    last_error = str(e)
                    time.sleep(1.0)
            if raw_answer:
                break

        if not raw_answer:
            raw_answer = f"Error generating answer: {last_error}"
            
        refusal_phrase = "don't have enough information"
        is_refusal = refusal_phrase.lower() in raw_answer.lower()

        return {
            "answer": raw_answer if raw_answer else "I don't have enough information in the provided documents to answer this question.",
            "sources": [] if is_refusal else sources,
            "has_sufficient_context": not is_refusal,
            "confidence": "Insufficient Evidence" if is_refusal else ("High" if top_results[0][1] >= 0.65 else "Medium")
        }
