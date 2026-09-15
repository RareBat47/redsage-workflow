"""Retrieval facade for evidence, findings, and reporting guidance."""
from __future__ import annotations
from typing import Any
from KB.assessment_retrieval_service import search_assessment_kb

_REPORTING_TERMS = ("evidence", "finding", "report", "remediation", "severity", "reproduction", "false positive", "cvss", "cwe")


def search_reporting_guidance(query: str, *, top_k: int = 8, **kwargs: Any) -> dict[str, Any]:
    if not any(term in query.lower() for term in _REPORTING_TERMS):
        query = f"evidence findings reporting remediation {query}"
    result = search_assessment_kb(query, top_k=top_k, **kwargs)
    result["kb_domain"] = "evidence_findings_reporting"
    return result
