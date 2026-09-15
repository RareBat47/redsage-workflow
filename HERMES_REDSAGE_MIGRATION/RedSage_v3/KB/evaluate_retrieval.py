"""Run deterministic evaluation checks against a supplied retrieval output."""
from __future__ import annotations
import json
from pathlib import Path
from KB.evaluation import load_cases, evaluate_case_output

if __name__ == "__main__":
    cases = load_cases()
    results = []
    for case in cases:
        results.append({"id": case["id"], "status": "pending", "problem": case["problem"]})
    path = Path("data/kb_build/evaluation_results.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"case_count": len(results), "results": results}, indent=2), encoding="utf-8")
    print(json.dumps({"case_count": len(results), "status": "ready_for_model_outputs", "path": str(path)}, indent=2))
