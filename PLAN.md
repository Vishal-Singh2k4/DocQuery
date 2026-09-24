# 5-Phase Implementation Plan: Secure PDF RAG System (DocQuery)

---

## 1. Executive Summary & Strategy

This document outlines the strict **5-Phase Implementation Plan** to build, evaluate, and deploy the Secure PDF RAG Question-Answering System.

### Key Objectives
1. **Strict Context Grounding:** Answers are generated **exclusively** from uploaded PDF documents. Zero outside LLM speculation.
2. **Granular Citations:** Exact document name and page number attribution for every generated answer.
3. **Anti-Hallucination Guardrail:** Explicit refusal when information is absent from the documents.
4. **10-Question CyanoFabric Benchmark:** Automated evaluation testing factual accuracy and refusal verification.
5. **Modern Minimalist React + TypeScript UI:** Built in strict compliance with clean, anti-bloat design principles (no emojis, no purple gradients, no drop shadows, 1 accent color, 1 corner radius, left-aligned typography).
6. **Free-Tier Deployment:** Decoupled architecture on **Netlify** (Frontend) and **Render / Hugging Face Spaces** (Backend).

---

## 2. Strict Frontend Design Rules (Linear / Vercel Minimalist Standard)

The frontend must adhere strictly to the following design system constraints:

| Category          | Rule                                       | Implementation Specification                       |
|:------------------|:-------------------------------------------|:---------------------------------------------------|
| **Alignment**     | ❌ Stop centering all text                 | Left-align all headings, body text, and cards      |
| **Line Length**   | ✅ Max 70 characters / line                | Set `max-width: 68ch` on prose and answer text     |
| **Spacing**       | ✅ Generous white space                    | Consistent 16px / 24px / 32px padding and gutters  |
| **Visuals**       | ✅ Real UI & document previews             | Real document badges; zero generic illustrations   |
| **Gradients**     | ❌ Remove purple gradients                 | Solid neutral surfaces; zero AI purple gradients   |
| **Borders**       | ✅ One uniform corner radius               | Exactly `border-radius: 6px` across all elements   |
| **Backgrounds**   | ❌ Remove floating blobs & circles         | Clean flat neutral dark background (`#0b0f17`)     |
| **Typography**    | ✅ Pair display & body font                | Inter for body, Space Grotesk / Geist for headings |
| **Color Palette** | ✅ Exactly one accent color                | Deep neutral slate theme + crisp cobalt (`#2563eb`)|
| **Interactions**  | ❌ No gimmicky hover effects               | Subtle, functional opacity / border transitions    |
| **Iconography**   | ✅ Phosphor / Lucide icon set              | Crisp monochrome SVG line icons only               |
| **Animations**    | ❌ Remove scroll animations                | Zero fade-in-on-scroll / parallax distractions     |
| **Type Scale**    | ✅ Real proportional type scale            | 12px (caps), 14px (body), 16px, 20px, 24px         |
| **Tone**          | ❌ Kill the emojis                         | Zero playful emojis in buttons, badges, or headers |
| **Text Styling**  | ❌ Remove gradient text                    | Solid high-contrast text (`#f8fafc` & `#94a3b8`)   |
| **Empty States**  | ✅ Thoughtfully designed empty states      | Explicit empty state views for upload, chat, eval  |
| **Elevation**     | ❌ No drop shadows                         | Flat surfaces defined by clean `1px border` rules  |

---

## 3. Technology Stack

| Layer            | Technology                   | Primary Purpose                        |
|:-----------------|:-----------------------------|:---------------------------------------|
| API Backend      | FastAPI (Python 3.10+)       | Async REST endpoints & OpenAPI schemas |
| Web Frontend     | React 18 + TypeScript (Vite) | Typed UI screens matching JD           |
| PDF Extraction   | pypdf                        | Page-by-page text & metadata parsing   |
| Embeddings & LLM | Google Gemini Free API       | Dense embeddings & grounded inference  |
| Vector Database  | In-Memory Numpy / ChromaDB   | Fast cosine similarity search          |
| Data Contracts   | Pydantic v2 & TypeScript     | Full-stack typed request & response    |
| Guardrails       | Cosine Threshold Filter      | Rejection when similarity < 0.40       |
| Evaluation Suite | Automated Benchmark Engine   | 10-question evaluation & scoring       |
| Cloud Hosting    | Netlify + Render / HF Spaces | 100% Free decoupled cloud deployment   |

---

## 4. Phase-by-Phase Implementation Breakdown

### Phase 1: PDF Ingestion & Embedding Pipeline
* **Goal:** Extract text from PDFs page-by-page, chunk with metadata, and generate dense vectors.
* **Tasks:**
  1. Initialize Python virtual environment with `fastapi`, `uvicorn`, `pypdf`, `google-genai`, `pydantic`.
  2. Implement `backend/rag_engine.py`:
     * Read uploaded PDF bytes using `pypdf`.
     * Preserve 1-indexed page numbers and document filename.
     * Implement sliding-window chunker (~450 chars, 50 chars overlap) with chunk ID tags.
     * Connect to Google Gemini API (`gemini-embedding-001`) for batch vector embeddings.
  3. Validate embedding generation on sample text in under 1 second.
* **Milestone:** Ingestion and vector generation fully verified via CLI test script (`test_phase1.py`).

---

### Phase 2: Guardrails, Refusal Engine & Evaluation Suite
* **Goal:** Implement evidence-grounded generation, anti-hallucination refusal, and the 10-question benchmark.
* **Tasks:**
  1. Build retrieval logic computing cosine similarity across stored chunks.
  2. Implement **Guardrail Rules**:
     * If top similarity score is below threshold (`< 0.40`), short-circuit with refusal: *"I don't have enough information in the provided documents to answer this question."*
     * Enclose retrieved context in `<document_context>` XML tags to isolate potential prompt injections.
  3. Wire `gemini-3.1-flash-lite` with strict system prompt forcing citations.
  4. Create `backend/benchmark.json` containing the 10 CyanoFabric test questions.
  5. Implement evaluation runner that computes factual match and confirms rejection of question #10.
* **Milestone:** CLI evaluation runs all 10 questions and outputs an automated scorecard (100% accuracy).

---

### Phase 3: FastAPI Web Service & Typed Contracts
* **Goal:** Expose high-performance REST API endpoints with Pydantic schemas and CORS support.
* **Tasks:**
  1. Define Pydantic models in `backend/schemas.py`:
     * `QueryRequest`, `SourceCitation`, `QueryResponse`
     * `EvalResultItem`, `EvalSummary`
  2. Implement `backend/server.py`:
     * `POST /api/upload`: Accepts multipart PDF, processes chunks, returns status and chunk count.
     * `POST /api/query`: Runs semantic search, guardrail check, and returns structured citation response.
     * `POST /api/evaluate`: Runs the 10-question benchmark and returns evaluation metrics.
     * `GET /api/health`: Confirms service health and loaded document count.
  3. Enable FastAPI CORS middleware for frontend communication.
* **Milestone:** Interactive Swagger UI (`/docs`) operational with all endpoints tested.

---

### Phase 4: React + TypeScript Dashboard (Minimalist Design System)
* **Goal:** Build the frontend matching the strict design rules (no emojis, left-aligned, 1 accent color, 1 corner radius, flat 1px borders).
* **Tasks:**
  1. Scaffold `frontend/` using Vite (`npm create vite@latest frontend -- --template react-ts`).
  2. Define TypeScript types in `frontend/src/types.ts` mirroring backend schemas.
  3. Build components:
     * `UploadCard.tsx`: Left-aligned dropzone with file name, page count, and status badge.
     * `ChatPanel.tsx`: Question input with 68ch line length, answer container, and clean source badges (Document Name, Page Number).
     * `BenchmarkPanel.tsx`: 1-click evaluation trigger displaying test summary table and accuracy percentage.
     * Empty states for each view when no document or query is active.
  4. Apply uniform `border-radius: 6px`, 1px borders, Inter font, and `#2563eb` accent.
* **Milestone:** Fully functional, typed React UI running locally connected to the FastAPI backend.

---

### Phase 5: Free Cloud Deployment, Testing & Demo Script
* **Goal:** Deploy the full-stack system for free, run end-to-end regression tests, and prepare the demo guide.
* **Tasks:**
  1. Configure `netlify.toml` for frontend deployment with API proxy rewrites.
  2. Create lightweight `Dockerfile` or Render build script for the FastAPI backend.
  3. Ingest the CyanoFabric Job Description PDF and record live query responses.
  4. Write `README.md` containing:
     * Architecture breakdown & design decisions
     * Guardrail & prompt injection mitigation strategy
     * Evaluation benchmark results table
     * 5-minute interview walkthrough script
* **Milestone:** Publicly accessible URL on Netlify + reproducible GitHub repository ready for review.

---

## 5. File Structure

```
DocQuery/
├── backend/
│   ├── server.py                # FastAPI app & REST routes
│   ├── rag_engine.py            # PDF loader, chunker, embeddings, & guardrails
│   ├── schemas.py               # Pydantic data models
│   ├── benchmark.json           # 10 ground-truth CyanoFabric test questions
│   ├── evaluate.py              # Automated test harness runner
│   ├── test_phase1.py           # Verification script for PDF loader & chunker
│   ├── requirements.txt         # fastapi, uvicorn, pypdf, google-genai, pydantic
│   └── .env.example             # GEMINI_API_KEY template
├── frontend/                    # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadCard.tsx   # Left-aligned PDF dropzone & metadata
│   │   │   ├── ChatPanel.tsx    # Q&A view with source page citations
│   │   │   └── BenchmarkPanel.tsx # 1-click evaluation scorecard
│   │   ├── types.ts             # TypeScript interfaces matching backend
│   │   ├── App.tsx              # Main dashboard layout
│   │   └── index.css            # Minimalist 1px border, 6px radius design
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── documents/
│   └── CyanoFabric_Job_Description.pdf # Benchmark evaluation document
├── netlify.toml                 # Netlify build & rewrite configuration
├── PLAN.md                      # This 5-phase plan
└── README.md                    # Setup, architecture & interview demo script
```

---

## 6. The 10-Question Ground Truth Evaluation Set

| ID | Test Question                                      | Expected Ground Truth                                   | Target Page |
|:---|:---------------------------------------------------|:--------------------------------------------------------|:------------|
| 1  | How many Product Engineering positions are open?   | 7 positions                                             | Page 1      |
| 2  | What programming languages are required?           | Python or TypeScript                                    | Page 1      |
| 3  | What does the internship convert to?               | Product Engineer                                        | Page 1      |
| 4  | What LLM concepts should applicants understand?    | Tokens, context windows, embeddings and tool calling    | Page 1      |
| 5  | What security framework should applicants know?    | OWASP Top 10                                            | Page 1      |
| 6  | What database technology is mentioned?             | PostgreSQL                                              | Page 1      |
| 7  | What frontend technology is mentioned?             | React                                                   | Page 1      |
| 8  | What skills are listed as good-to-have?            | RAG/agent frameworks, Docker, cloud, Ollama or vLLM     | Page 1      |
| 9  | What are the core functional areas of the role?    | AI, agentic AI and cybersecurity                        | Page 1      |
| 10 | What is CyanoFabric's annual revenue?              | Refusal: Information not available in the document      | N/A         |
