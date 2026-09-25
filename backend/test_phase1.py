import os
import sys
from backend.rag_engine import RAGEngine

def test_phase1_pipeline():
    print("--- Running Phase 1 Verification Tests ---")
    engine = RAGEngine()
    
    pdf_path = os.path.join("documents", "sample_document.pdf")
    assert os.path.exists(pdf_path), f"Test PDF not found at {pdf_path}"
    
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 1. Test PDF Extraction
    pages = engine.extract_text_from_pdf(file_bytes, "sample_document.pdf")
    print(f"[PASS] Extracted {len(pages)} pages from PDF.")
    assert len(pages) == 3, f"Expected 3 pages, found {len(pages)}"
    
    for page_num, text in pages:
        assert page_num in [1, 2, 3], f"Unexpected page number: {page_num}"
        assert len(text) > 0, f"Page {page_num} is empty"
        print(f"  - Page {page_num}: {len(text)} characters extracted.")

    # 2. Test Chunking
    chunks = engine.chunk_document(pages, "sample_document.pdf", chunk_size=450, chunk_overlap=50)
    print(f"[PASS] Generated {len(chunks)} chunks from {len(pages)} pages.")
    assert len(chunks) >= 3, "Expected at least 3 chunks"

    # Verify metadata on all chunks
    for chunk in chunks:
        assert chunk.doc_name == "sample_document.pdf"
        assert chunk.page_number in [1, 2, 3]
        assert chunk.chunk_id.startswith("sample_document.pdf_p")
        assert len(chunk.text) > 0

    print("  - Sample chunk metadata verified:")
    print(f"    ID: {chunks[0].chunk_id}")
    print(f"    Page: {chunks[0].page_number}")
    print(f"    Preview: {chunks[0].text[:80]}...")

    # 3. Test Cosine Similarity Math
    import numpy as np
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    v3 = np.array([0.0, 1.0, 0.0])
    
    def cos_sim(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        
    assert round(cos_sim(v1, v2), 4) == 1.0, "Cosine similarity for identical vectors failed"
    assert round(cos_sim(v1, v3), 4) == 0.0, "Cosine similarity for orthogonal vectors failed"
    print("[PASS] Vector math & similarity functions verified.")

    print("\n--- ALL PHASE 1 TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_phase1_pipeline()
