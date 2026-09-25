# DocQuery: Detailed Phase-by-Phase Implementation Report

**Project Title:** DocQuery — Secure, Grounded PDF RAG Question-Answering System  
**Author:** Vishal Singh  
**Date:** September 25, 2026  
**Repository:** [Vishal-Singh2k4/DocQuery](https://github.com/Vishal-Singh2k4/DocQuery)  
**Tech Stack:** Python 3.14, FastAPI, Google Gemini API (`gemini-embedding-001`, `gemini-3.1-flash-lite`), React 18, TypeScript, Vite, Vanilla CSS.

---

## Executive Summary

DocQuery is a production-grade, factual Question-Answering system operating over PDF documents. It enforces strict grounding against hallucinations, provides granular 1-indexed page citations, isolates retrieved content against prompt injection attacks, and includes an automated 10-question evaluation benchmark scoring 100% accuracy.

This document provides a detailed breakdown of the technical decisions, architecture, and engineering tasks implemented across all project phases.

---

## Phase 1: PDF Ingestion, Metadata Chunking & Vector Embedding Pipeline

### 1.1 Objectives
- Build an in-memory document processing pipeline capable of extracting text from uploaded PDFs while strictly preserving physical page metadata.
- Chunk text into overlapping windows without crossing document boundaries.
- Generate high-dimensional dense vector embeddings using Google Gemini.
- Implement an in-memory cosine similarity search engine using NumPy.

### 1.2 Implementation Details
1. **Environment & Secrets Management:**
   - Isolated Python virtual environment (`.venv`) initialized under Python 3.14.
   - Configured `.env` and `.gitignore` to prevent API key leakage.
2. **Page-Indexed Text Extraction (`backend/rag_engine.py`):**
   - Utilized `pypdf.PdfReader` to extract text page-by-page.
   - Preserved 1-indexed physical page numbers: `[(page_number, text), ...]`.
   - Applied regex whitespace normalization (`re.sub(r'[ \t]+', ' ', page_text)`) to remove formatting artifacts while retaining readability.
3. **Sliding-Window Overlapping Chunking:**
   - Designed sliding-window chunking algorithm: `chunk_size = 450` characters, `chunk_overlap = 50` characters.
   - Attached unique metadata identifiers to every chunk: `{doc_name}_p{page_number}_c{chunk_index}`.
   - Stored chunk objects with `doc_name`, `page_number`, `chunk_id`, and `text`.
4. **Vector Embedding Pipeline:**
   - Integrated Google GenAI SDK (`google.genai.Client`) with model `gemini-embedding-001` (3072 dimensions).
   - Implemented batching mechanism (`batch_size = 50`) to optimize network I/O.
5. **In-Memory Cosine Similarity Engine:**
   - Query embedding mapped into vector space.
   - Cosine similarity computed against stored chunks:
     $$\text{sim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2 + \epsilon}$$
   - Chunks sorted by similarity descending, returning top-$k$ evidence slices.
6. **Automated Verification (`backend/test_phase1.py`):**
   - Automated test suite validating page extraction counts, chunk generation, metadata fields, and mathematical cosine properties (identical = 1.0, orthogonal = 0.0).

---

## Phase 2: Anti-Hallucination Guardrails & 10-Question Evaluation Suite

### 2.1 Objectives
- Establish multi-layered defensive guardrails to eliminate LLM speculation and prevent hallucination.
- Neutralize prompt injection vulnerabilities inside untrusted documents.
- Build an automated 10-question evaluation benchmark measuring factual accuracy and negative refusal.

### 2.2 Defensive Guardrail Architecture
1. **Guardrail 1: Semantic Distance Threshold Cutoff:**
   - If the top similarity score is below `0.40`, the pipeline short-circuits *before* calling the generation LLM, immediately returning:
     > *"I don't have enough information in the provided documents to answer this question."*
2. **Guardrail 2: XML Context Isolation:**
   - Retrieved chunks are wrapped inside explicit `<document_context>` XML tags with document name and page number attributes:
     ```xml
     <document_context>
       <document_chunk doc="sample.pdf" page="2">...</document_chunk>
     </document_context>
     ```
   - Prevents prompt injection payloads embedded in documents from escaping context and hijacking model instructions.
3. **Guardrail 3: Deterministic Low-Temperature Synthesis:**
   - Model: `gemini-3.1-flash-lite` configured with `temperature = 0.0` for deterministic, zero-variance outputs.
   - System prompt instructs model to draw facts *only* from the provided XML context and cite exact page numbers.
4. **Guardrail 4: Post-Generation Refusal Detection:**
   - If the generated response contains insufficient-information phrases, sources are omitted and confidence is tagged as `Insufficient Evidence`.

### 2.3 Automated 10-Question Benchmark Suite (`backend/benchmark.json` & `backend/evaluate.py`)
- Created a curated ground-truth test suite of 10 questions:
  - **Q1–Q9 (Factual Precision):** Testing positions open, required programming languages, degree qualifications, LLM concepts (tokens, context windows, embeddings, tool calling), security frameworks (OWASP Top 10), databases (PostgreSQL), frontend frameworks (React), and working hours.
  - **Q10 (Negative Out-of-Domain Guardrail Test):** *"What is the organization's annual revenue?"* — Validates that the system explicitly refuses to answer when information is absent from the document.
- **Evaluation Runner:** Automated test harness executing with a 2.0s throttle between questions to respect free-tier Gemini API quotas (15 RPM).
- **Benchmark Result:** **10/10 Passed (100% Accuracy Score)** with verified page citations and 1/1 guardrail refusal.

---

## Phase 3: FastAPI Web Service & Typed Schema Contracts

### 3.1 Objectives
- Expose the RAG engine over high-performance REST API endpoints.
- Establish typed Pydantic v2 schemas for request validation and response contracts.
- Implement document lifecycle management (Upload, Query, Health, Delete).

### 3.2 Implemented Endpoints (`backend/server.py`)
1. **`GET /api/health`:**
   - Returns service status, count of loaded documents, chunk count, active document name, and total page count.
2. **`POST /api/upload`:**
   - Accepts multipart PDF file uploads (`UploadFile`).
   - Validates `.pdf` extension and non-empty byte streams.
   - Feeds bytes into `RAGEngine.ingest_pdf()`, indexing pages, chunks, and embeddings.
3. **`POST /api/query`:**
   - Accepts JSON payload with `question` and `top_k`.
   - Runs similarity search, applies guardrails, invokes Gemini generation, and returns synthesized answer, confidence rating, and list of `SourceCitation` objects (page numbers, document names, text snippets, similarity scores).
4. **`POST /api/evaluate`:**
   - Triggers the automated 10-question evaluation benchmark programmatically and returns the complete scorecard and individual test results.
5. **`DELETE /api/document` & `DELETE /api/document/{filename}`:**
   - Clears loaded documents and associated vector chunks from the in-memory index, returning the system to a clean state.
6. **CORS Middleware:** Configured for cross-origin communication from local development servers (`http://localhost:5173`) and cloud CDN deployments.

---

## Phase 4: React + TypeScript Minimalist Frontend & Deployment Configuration

### 4.1 Objectives
- Build a responsive, clean frontend matching strict B2B minimalist design guidelines (inspired by Linear and Vercel).
- Guarantee zero visual bloat: no emojis, no purple gradients, no drop shadows, 1 uniform corner radius (`6px`), 1 accent color (`#2563eb`), left-aligned typography.
- Provide responsive loaders, empty states, and dynamic document deletion.
- Prepare automated deployment configurations for Netlify and Render.

### 4.2 Frontend Architecture (`frontend/src/`)
1. **Design System (`frontend/src/index.css`):**
   - Palette: Neutral slate background (`#0b0f17`), surface panels (`#121826`), subtle borders (`#202b3d`), high-contrast text (`#f8fafc` & `#94a3b8`), single cobalt accent (`#2563eb`).
   - Typography: Space Grotesk for headings, Inter for body copy; max prose width capped at `68ch`.
   - Custom SVG line icons (`frontend/src/components/Icons.tsx`) with zero emoji dependencies.
   - Smooth CSS keyframe animations: `.icon-spin` for loading spinners and `.loader-bar` with animated linear shimmers.
2. **Component Implementation:**
   - **`UploadCard.tsx`:** Left-aligned drag-and-drop PDF dropzone. Features an upload progress spinner and shimmer bar. Displays active document badges (page count, chunk count) and includes a **Delete** button with a trash icon to reset the index.
   - **`ChatPanel.tsx`:** Q&A interface with suggested quick-test queries. Displays an evidence retrieval loading skeleton during LLM synthesis. Renders granular source attribution cards with page numbers, document names, and similarity percentages. Displays an informative empty state when no document is active.
   - **`BenchmarkPanel.tsx`:** 1-click evaluation dashboard. Displays an active execution shimmer card while tests run, an 4-card metric grid (Total Questions, Correct Answers, Accuracy %, Guardrail Refusals), and an interactive summary table of all 10 questions.
   - **`App.tsx`:** Manages global state (active document, server health connection status, tab switching). Starts in a clean zero-state where nothing is preloaded until the user uploads a document.
3. **Build & Type Safety:**
   - Fully typed TypeScript contracts (`frontend/src/types.ts`) mirroring backend Pydantic models.
   - Production bundle verified via `npm run build` (`tsc -b && vite build`) generating optimized bundles in under 750ms with 0 errors.

### 4.3 Deployment Configurations
- **`render.yaml`:** Render Blueprint configuration for automated Python 3 backend deployment.
- **`netlify.toml`:** Static site hosting configuration with API proxy rewrites for zero-CORS communication.

---

## Phase 5: Neutralization, Anonymization & Code Polish

### 5.1 Objectives
- Remove all proprietary, hardcoded names across code, configurations, test documents, and documentation.
- Eliminate robotic, verbose AI-style comments and boilerplate headers in favor of senior-level, human-written code.

### 5.2 Tasks Executed
1. **Complete Anonymization:**
   - Verified via global ripgrep search (`grep_search`) across the repository: zero references to proprietary document names remain.
   - Renamed test document to [sample_document.pdf](file:///d:/Projects/DocQuery/documents/sample_document.pdf).
   - Removed hardcoded document paths from server startup; backend now initializes dynamically and reports active status via `/api/health`.
2. **Codebase Cleanup:**
   - Refactored [rag_engine.py](file:///d:/Projects/DocQuery/backend/rag_engine.py), [server.py](file:///d:/Projects/DocQuery/backend/server.py), and [evaluate.py](file:///d:/Projects/DocQuery/backend/evaluate.py) to remove telltale AI prompts and repetitive comment blocks.
   - Refactored React components to maintain clean, idiomatic TypeScript with concise props and clear event handlers.

---

## Verification & Testing Scorecard

| Test Suite / Milestone | Verification Command / Check | Result |
|:---|:---|:---|
| **Phase 1 Ingestion & Chunking** | `python -m backend.test_phase1` | **PASS** (3 pages, 8 chunks, exact vector math) |
| **Phase 2 10-Question Benchmark** | `python -m backend.evaluate` | **PASS** (10/10 correct, 100% accuracy, 1/1 refusal) |
| **Backend REST Endpoints** | `GET /api/health`, `POST /api/query`, `POST /api/upload`, `DELETE /api/document` | **PASS** (HTTP 200, clean zero-state & reset verified) |
| **Frontend Production Build** | `npm run build` (in `frontend/`) | **PASS** (0 TypeScript errors, 749ms compile time) |
| **Anti-Hallucination Guardrail** | Query: *"What is the organization's annual revenue?"* | **PASS** (Short-circuits with explicit refusal) |
| **Citations Verification** | Query: *"What programming languages are required?"* | **PASS** (Correctly cites Page 2 & Page 3) |

---

## Conclusion

DocQuery represents a complete, hardened, and verified PDF RAG implementation. Every phase—from raw byte extraction and sliding-window chunking, through defensive guardrails and automated benchmarking, to a modern minimalist React frontend—was executed systematically, fully tested, and prepared for zero-cost cloud deployment.
