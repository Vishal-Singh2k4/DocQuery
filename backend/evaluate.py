import os
import json
import time
from typing import Dict, Any, List
from backend.rag_engine import RAGEngine
from backend.schemas import EvalSummary, EvalResultItem, SourceCitation

def run_evaluation(pdf_path: str = None, benchmark_path: str = "backend/benchmark.json") -> EvalSummary:
    print("\n=======================================================")
    print("        RAG PIPELINE EVALUATION BENCHMARK SUITE        ")
    print("=======================================================\n")

    if not pdf_path:
        docs_dir = "documents"
        pdf_candidates = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.lower().endswith(".pdf")] if os.path.exists(docs_dir) else []
        if not pdf_candidates:
            raise FileNotFoundError("No evaluation document found in documents/ directory.")
        pdf_path = pdf_candidates[0]

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
    if not os.path.exists(benchmark_path):
        raise FileNotFoundError(f"Benchmark file not found at {benchmark_path}")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # Initialize RAG Engine and Ingest PDF
    engine = RAGEngine()
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    filename = os.path.basename(pdf_path)
    print(f"[*] Ingesting and embedding document: {filename}...")
    ingest_result = engine.ingest_pdf(pdf_bytes, filename)
    print(f"[+] Document processed: {ingest_result['total_pages']} pages, {ingest_result['total_chunks']} chunks indexed.\n")

    results: List[EvalResultItem] = []
    correct_count = 0
    rejected_count = 0

    print(f"[*] Running automated benchmark on {len(questions)} test questions...\n")

    for item in questions:
        q_id = item["id"]
        question = item["question"]
        expected = item["expected_answer"]
        is_unsupported = item["is_unsupported"]

        start_time = time.time()
        res = engine.query(question, top_k=3)
        elapsed = round(time.time() - start_time, 2)

        actual_answer = res["answer"]
        has_context = res["has_sufficient_context"]
        sources = [SourceCitation(**s) for s in res.get("sources", [])]

        is_correct = False
        refusal_triggered = not has_context or ("don't have enough information" in actual_answer.lower())

        if is_unsupported:
            # Negative Guardrail Test: MUST trigger refusal
            if refusal_triggered:
                is_correct = True
                rejected_count += 1
        else:
            # Factual Q&A: Must NOT refuse and must contain key phrases
            if not refusal_triggered:
                # Check keyword overlap or key factual terms
                keywords = [k.strip().lower() for k in expected.split() if len(k) > 3]
                matches = sum(1 for kw in keywords if kw in actual_answer.lower())
                # If at least 40% of keywords match or direct substring present
                if matches >= max(1, len(keywords) * 0.4) or expected.lower() in actual_answer.lower():
                    is_correct = True

        if is_correct:
            correct_count += 1

        status_tag = "[PASS]" if is_correct else "[FAIL]"
        print(f"Q{q_id:02d} {status_tag} {question} ({elapsed}s)", flush=True)
        print(f"     Expected: {expected}", flush=True)
        print(f"     Actual:   {actual_answer}", flush=True)
        if sources:
            cited_pages = list(set(s.page_number for s in sources))
            print(f"     Cited Pages: {cited_pages}", flush=True)
        print("-" * 55, flush=True)

        results.append(EvalResultItem(
            question_id=q_id,
            question=question,
            expected=expected,
            actual=actual_answer,
            is_correct=is_correct,
            refusal_triggered=refusal_triggered,
            sources=sources
        ))
        # Rate-limiting throttle for free-tier quota (15 RPM)
        time.sleep(2.0)

    accuracy = round((correct_count / len(questions)) * 100, 1)

    print("\n=======================================================")
    print("                 BENCHMARK SCORECARD                   ")
    print("=======================================================")
    print(f"Total Questions Evaluated:         {len(questions)}")
    print(f"Correct Answers:                   {correct_count}")
    print(f"Incorrect Answers:                 {len(questions) - correct_count}")
    print(f"Overall Accuracy:                  {accuracy}%")
    print(f"Unsupported Questions Rejected:    {rejected_count}/1")
    print("=======================================================\n")

    return EvalSummary(
        total=len(questions),
        correct=correct_count,
        accuracy_percent=accuracy,
        unsupported_rejected=rejected_count,
        results=results
    )

if __name__ == "__main__":
    run_evaluation()
