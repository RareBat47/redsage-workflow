"""Run retrieval-only checks for internal workflow-generation cases."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from KB.workflow_retrieval_service import search_workflow_context  # noqa: E402
from KB.evaluation import load_cases  # noqa: E402

# This file is also executable directly; the package/module name collision is avoided.


if __name__ == "__main__":
    results = []
    for case in load_cases():
        try:
            response = search_workflow_context(case["problem"], actor_type="evaluation")
            results.append({
                "id": case["id"],
                "status": "retrieved",
                "citation_count": len(response["citations"]),
                "query_id": response["query_id"],
                "top_paths": [c["path"] for c in response["citations"][:3]],
            })
        except Exception as error:
            results.append({"id": case["id"], "status": "error", "error": str(error)})
    output = ROOT / "data" / "kb_build" / "retrieval_evaluation_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"case_count": len(results), "results": results}, indent=2), encoding="utf-8")
    print(json.dumps({"case_count": len(results), "output": str(output), "statuses": [r["status"] for r in results]}, indent=2))
