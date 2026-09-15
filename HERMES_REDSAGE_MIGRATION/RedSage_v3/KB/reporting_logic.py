"""Evidence-to-finding preparation for the internal reporting KB."""
from __future__ import annotations
from typing import Any


def classify_evidence_strength(context: dict[str, Any]) -> dict[str, Any]:
    missing = []
    if not str(context.get("scope", "")).lower() in {"locked", "authorized"}:
        missing.append("scope")
    if not str(context.get("evidence", "")).strip():
        missing.append("evidence")
    if not str(context.get("reproduction", "")).strip():
        missing.append("reproduction")
    return {
        "status": "READY_FOR_REVIEW" if not missing else "INSUFFICIENT_EVIDENCE",
        "missing": missing,
        "confirmation_allowed": not missing,
    }


def build_finding_record(title: str, context: dict[str, Any]) -> dict[str, Any]:
    assessment = classify_evidence_strength(context)
    return {
        "title": title,
        "status": "DRAFT",
        "confirmation_allowed": assessment["confirmation_allowed"],
        "missing": assessment["missing"],
        "evidence_summary": str(context.get("evidence", ""))[:800],
        "reproduction_summary": str(context.get("reproduction", ""))[:800],
    }
