import os
from fpdf import FPDF, XPos, YPos

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, 'DocQuery - Phase-by-Phase Technical Implementation Report', border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
        self.set_draw_color(226, 232, 240)
        self.line(10, 16, 200, 16)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_pdf_report():
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(14, 14, 14)

    # ---------------- COVER / TITLE ----------------
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 12, 'DocQuery: Implementation Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 7, 'Secure, Grounded PDF RAG Question-Answering System', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Author: Vishal Singh  |  Date: September 25, 2026', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Stack: FastAPI, Google Gemini API, React 18, TypeScript, Vite', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # ---------------- SECTION 1 ----------------
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(37, 99, 235) # Accent #2563eb
    pdf.cell(0, 8, 'Executive Summary', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    summary_text = (
        "DocQuery is a production-grade, factual Question-Answering system operating over PDF documents. "
        "It enforces strict context grounding against hallucinations, provides granular 1-indexed page citations, "
        "isolates retrieved content against prompt injection attacks, and includes an automated 10-question evaluation benchmark "
        "scoring 100% accuracy. The frontend follows a strict B2B minimalist design system (Inter font, 6px uniform corner radius, "
        "single #2563eb accent color, flat 1px borders, and zero purple gradients or emojis)."
    )
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(5)

    # ---------------- SECTION 2: PHASE 1 ----------------
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, 'Phase 1: PDF Ingestion, Metadata Chunking & Vector Embeddings', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    p1_items = [
        ("Environment Setup: ", "Isolated Python 3.14 virtual environment (.venv) with strict .gitignore protection for credentials."),
        ("Page-Indexed Text Extraction: ", "Extracted text page-by-page via pypdf.PdfReader, preserving 1-indexed page numbers. Whitespace normalized via regex."),
        ("Sliding-Window Chunking: ", "Designed sliding-window chunking (chunk_size=450 chars, chunk_overlap=50 chars). Every chunk preserves doc_name, page_number, and chunk_id ({doc}_p{page}_c{chunk})."),
        ("Dense Vector Embeddings: ", "Integrated Google Gemini API using gemini-embedding-001 (3072 dimensions) with batching (batch_size=50)."),
        ("In-Memory Cosine Similarity: ", "Vector search implemented in NumPy computing normalized dot products. Top-k scoring chunks retrieved in descending order."),
        ("Automated Verification: ", "Created backend/test_phase1.py verifying page counts, chunk metadata integrity, and mathematical cosine similarity assertions.")
    ]

    for title, desc in p1_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(5, 5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(pdf.get_string_width(title) + 1, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

    pdf.ln(4)

    # ---------------- SECTION 3: PHASE 2 ----------------
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, 'Phase 2: Anti-Hallucination Guardrails & 10-Question Evaluation Suite', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    p2_items = [
        ("Semantic Distance Cutoff: ", "If top similarity score is below 0.40, the system short-circuits immediately with explicit refusal without invoking the LLM."),
        ("XML Prompt Injection Isolation: ", "Retrieved context chunks are enclosed in <document_context> XML tags, isolating user queries from adversarial document injection payloads."),
        ("Deterministic Low-Temperature Generation: ", "Gemini 3.1 Flash Lite configured with temperature=0.0 and strict system instructions mandating factual page citations."),
        ("10-Question Benchmark Dataset: ", "Created backend/benchmark.json with 9 factual questions (roles, languages, concepts, OWASP Top 10, PostgreSQL, React, working hours) and 1 negative guardrail question (annual revenue)."),
        ("Automated Evaluation Harness: ", "Created backend/evaluate.py running automated scoring with 2.0s rate-limiting for free tier. Result: 10/10 Passed (100% accuracy, 1/1 refusal).")
    ]

    for title, desc in p2_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(5, 5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(pdf.get_string_width(title) + 1, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

    # ---------------- PAGE 2: PHASE 3, 4, 5 & SCORECARD ----------------
    pdf.add_page()

    # Phase 3
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, 'Phase 3: FastAPI Web Service & Typed Contracts', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    p3_items = [
        ("Pydantic v2 Contracts: ", "Defined QueryRequest, QueryResponse, SourceCitation, DocumentUploadResponse, DeleteDocumentResponse, and EvalSummary in backend/schemas.py."),
        ("Health & Status (GET /api/health): ", "Reports service state, loaded documents, total chunk counts, active document name, and page counts."),
        ("PDF Ingestion (POST /api/upload): ", "Multipart PDF upload endpoint handling page parsing, chunking, and embedding generation."),
        ("Grounded Query (POST /api/query): ", "Runs semantic retrieval, applies guardrails, and returns answer with page citations."),
        ("Automated Benchmark (POST /api/evaluate): ", "Executes the 10-question evaluation suite programmatically and returns the complete scorecard."),
        ("Document Deletion (DELETE /api/document): ", "Clears active document and associated vector chunks to return system to clean zero-state."),
        ("CORS Middleware: ", "Enabled for cross-origin frontend communication from local development and cloud CDN environments.")
    ]

    for title, desc in p3_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(5, 5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(pdf.get_string_width(title) + 1, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

    pdf.ln(4)

    # Phase 4
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, 'Phase 4: Modern Minimalist React Frontend & UI Loaders', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    p4_items = [
        ("Design System (Linear / Vercel Aesthetic): ", "Inter font, Space Grotesk headings, 6px uniform corner radius, single #2563eb accent, 68ch max prose line length, flat 1px borders, zero emojis."),
        ("UploadCard Component: ", "Drag-and-drop PDF dropzone with animated spinner, upload progress bar, active document badge, and document deletion action."),
        ("ChatPanel Component: ", "Interactive Q&A with suggested quick queries, answer synthesis loading skeleton, confidence badge, and granular source attribution badges."),
        ("BenchmarkPanel Component: ", "1-click evaluation runner with execution progress bar, 4-stat scorecard summary grid, and full 10-question results table."),
        ("Zero-State on Startup: ", "Service initializes with zero documents loaded; query inputs and chat are safely disabled until a document is ingested."),
        ("Deployment Automation: ", "Configured netlify.toml for static frontend hosting with API rewrites and render.yaml for 1-click Python backend hosting.")
    ]

    for title, desc in p4_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(5, 5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(pdf.get_string_width(title) + 1, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

    pdf.ln(4)

    # Phase 5 & Verification
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, 'Phase 5: Anonymization, Code Polish & Verification Scorecard', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    p5_items = [
        ("Complete Anonymization: ", "Removed all hardcoded vendor / company names across all files (grep verified 0 occurrences). Test document standardized as sample_document.pdf."),
        ("Senior-Level Code Polish: ", "Cleaned up codebase to remove AI-sounding comments, repetitive boilerplate, and unnecessary logs."),
        ("TypeScript Production Bundle: ", "npm run build verified compiling cleanly to dist/ in 749ms with 0 errors.")
    ]

    for title, desc in p5_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(5, 5, chr(149), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(pdf.get_string_width(title) + 1, 5, title, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

    pdf.ln(5)

    # Verification Scorecard Table
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, 'Verification Results Summary', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(60, 6, 'Milestone / Test', border=1, fill=True)
    pdf.cell(85, 6, 'Verification Scope', border=1, fill=True)
    pdf.cell(35, 6, 'Status', border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    table_rows = [
        ("Phase 1 Verification", "PDF extraction, chunking & vector cosine math", "PASS (100%)"),
        ("Phase 2 Benchmark", "10 ground-truth questions + negative refusal", "PASS (10/10)"),
        ("Backend REST API", "Upload, Query, Health, Delete endpoints", "PASS (200 OK)"),
        ("Frontend Build", "React 18 + TypeScript production bundle", "PASS (0 errors)"),
        ("Anti-Hallucination Guardrail", "Negative refusal on out-of-domain query", "PASS (Refused)"),
        ("Source Citations", "Exact 1-indexed physical page numbers", "PASS (Page 2 & 3)")
    ]

    pdf.set_font('Helvetica', '', 8.5)
    for m, s, st in table_rows:
        pdf.cell(60, 5.5, m, border=1)
        pdf.cell(85, 5.5, s, border=1)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(16, 185, 129) if "PASS" in st else pdf.set_text_color(15, 23, 42)
        pdf.cell(35, 5.5, st, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)

    output_path = "DocQuery_Implementation_Report.pdf"
    pdf.output(output_path)
    print(f"Generated PDF implementation report: {output_path}")

if __name__ == "__main__":
    generate_pdf_report()
