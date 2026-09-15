"""Run end-to-end internal engagement workflow evaluations."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_case_in_fresh_process(case: dict, receipt_directory: Path) -> dict:
    payload = json.dumps({"case": case, "receipt_directory": str(receipt_directory)})
    code = (
        "import json,sys; "
        "from KB.engagement_evaluation import evaluate_case; "
        "p=json.loads(sys.stdin.read()); "
        "print(json.dumps(evaluate_case(p['case'], receipt_directory=p['receipt_directory'])))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        input=payload,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        check=False,
    )
    if completed.returncode != 0:
        return {
            "id": case["id"],
            "passed": False,
            "status": "ERROR",
            "error": completed.stderr.strip()[-2000:] or f"subprocess exit {completed.returncode}",
        }
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"id": case["id"], "passed": False, "status": "ERROR", "error": completed.stdout[-2000:]}


if __name__ == "__main__":
    cases = json.loads((ROOT / "data" / "kb_build" / "engagement_evaluation_cases.json").read_text(encoding="utf-8"))
    receipt_directory = ROOT / "data" / "kb_build" / "engagement_evaluation_receipts"
    results = [run_case_in_fresh_process(case, receipt_directory) for case in cases]
    output = {
        "suite": "internal_engagement_workflow_v1",
        "execution_isolation": "fresh_subprocess_per_case",
        "case_count": len(results),
        "passed_count": sum(item["passed"] for item in results),
        "all_passed": all(item["passed"] for item in results),
        "results": results,
    }
    path = ROOT / "data" / "kb_build" / "engagement_evaluation_results.json"
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"case_count": output["case_count"], "passed_count": output["passed_count"], "all_passed": output["all_passed"], "path": str(path)}, indent=2))
