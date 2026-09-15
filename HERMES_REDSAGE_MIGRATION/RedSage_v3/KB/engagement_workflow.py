"""End-to-end internal engagement workflow orchestration."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from KB.assessment_retrieval_service import search_assessment_kb
from KB.consolidated_roadmap_service import generate_consolidated_internal_roadmap
from KB.reporting_assessment import review_evidence


def run_internal_engagement_workflow(
    problem_statement: str,
    *,
    selected_step: str | None = None,
    evidence: dict[str, Any] | None = None,
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
    top_k: int = 8,
    receipt_directory: str | Path = "data/kb_build/engagement_receipts",
) -> dict[str, Any]:
    roadmap_result = generate_consolidated_internal_roadmap(
        problem_statement,
        environment_scope=environment_scope,
        target_type=target_type,
        top_k=top_k,
        receipt_directory=receipt_directory,
    )
    roadmap = roadmap_result["roadmap"]
    result: dict[str, Any] = {
        "workflow_status": roadmap["status"],
        "roadmap": roadmap,
        "roadmap_markdown": roadmap_result["markdown"],
        "roadmap_retrieval": roadmap_result["retrieval"],
        "step_guidance": None,
        "evidence_review": None,
    }
    if selected_step and roadmap["status"] == "READY_FOR_REVIEW":
        result["step_guidance"] = search_assessment_kb(
            f"{selected_step} for this authorized assessment: {problem_statement}",
            environment_scope=environment_scope,
            top_k=top_k,
            actor_type="operator",
            receipt_directory=receipt_directory,
        )
    if evidence is not None:
        result["evidence_review"] = review_evidence(evidence)
        if result["evidence_review"]["finding_draft"]["confirmation_allowed"] is False:
            result["workflow_status"] = "NEEDS_CLARIFICATION"
    return result
