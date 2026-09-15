"""Run offline evaluation checks for internal workflow roadmap retrieval."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from KB.evaluation import load_cases

if __name__ == "__main__":
    cases = load_cases()
    out = Path(__file__).resolve().parents[2] / "data" / "kb_build" / "evaluation_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for case in cases:
        results.append({
            "id": case["id"],
            "problem": case["problem"],
            "expected_terms": case["expected"]["must_include"],
            "status": "ready_for_retrieval_output",
        })
    data = {"suite": "workflow_generation_internal_v1", "case_count": len(results), "results": results}
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps({"case_count": len(results), "status": "ready_for_retrieval_output", "path": str(out)}, indent=2))
