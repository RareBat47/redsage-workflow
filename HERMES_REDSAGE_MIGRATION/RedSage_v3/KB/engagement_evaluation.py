"""End-to-end regression evaluation for the internal engagement workflow."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from KB.engagement_workflow import run_internal_engagement_workflow


def evaluate_case(case: dict[str, Any], *, receipt_directory: str | Path = "data/kb_build/evaluation_receipts") -> dict[str, Any]:
    expected_status = case["expected_status"]
    result = run_internal_engagement_workflow(
        case["problem"],
        selected_step=case.get("selected_step"),
        environment_scope=case.get("environment_scope", "authorized_engagement"),
        receipt_directory=receipt_directory,
    )
    roadmap = result["roadmap"]
    checks = {
        "status": result["workflow_status"] == expected_status,
        "roadmap_receipt": bool(roadmap.get("receipt_id")) if expected_status != "NEEDS_CLARIFICATION" else True,
        "clarifications": bool(roadmap.get("clarification_questions")) if expected_status == "NEEDS_CLARIFICATION" else True,
        "step_guidance": bool(result.get("step_guidance")) == bool(case.get("expect_step_guidance", False)),
        "safety": bool(roadmap.get("safety", {}).get("decision")),
    }
    return {"id": case["id"], "passed": all(checks.values()), "checks": checks, "status": result["workflow_status"], "receipt_id": roadmap.get("receipt_id")}


def evaluate_cases(cases: list[dict[str, Any]], *, receipt_directory: str | Path = "data/kb_build/evaluation_receipts") -> dict[str, Any]:
    results = [evaluate_case(case, receipt_directory=receipt_directory) for case in cases]
    return {"case_count": len(results), "passed_count": sum(item["passed"] for item in results), "all_passed": all(item["passed"] for item in results), "results": results}
