"""Reporting-domain retrieval and evidence review facade."""
from __future__ import annotations
from typing import Any
from KB.assessment_retrieval_service import search_assessment_kb
from KB.reporting_logic import classify_evidence_strength, build_finding_record


def review_evidence(context: dict[str, Any]) -> dict[str, Any]:
    strength = classify_evidence_strength(context)
    record = build_finding_record(str(context.get("title", "Untitled finding")), context)
    return {"evidence_assessment": strength, "finding_draft": record}


def search_reporting_context(query: str, **kwargs: Any) -> dict[str, Any]:
    result = search_assessment_kb(
        f"evidence findings reporting severity remediation false positives {query}",
        collection_name="redsage_v3_evidence_reporting_cohere_v1",
        **kwargs,
    )
    result["kb_domain"] = "evidence_findings_reporting"
    return result
