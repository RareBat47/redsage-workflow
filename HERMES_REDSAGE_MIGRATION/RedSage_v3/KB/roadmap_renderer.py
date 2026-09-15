"""Readable Markdown rendering for internal roadmap drafts."""
from __future__ import annotations
from typing import Any


def render_markdown_roadmap(roadmap: dict[str, Any]) -> str:
    lines = [
        "# Internal Workflow Roadmap",
        "",
        f"**Status:** {roadmap.get('status', 'UNKNOWN')}",
        f"**Target type:** {roadmap.get('target_type', 'unknown')}",
        f"**Environment:** {roadmap.get('environment_scope', 'unknown')}",
        f"**Receipt:** {roadmap.get('receipt_id') or 'not available'}",
        f"Receipt: {roadmap.get('receipt_id') or 'not available'}",
        f"**Classification:** {roadmap.get('query_classification', {}).get('primary', 'unknown')}",
        "",
        f"> **Safety:** {roadmap.get('safety', {}).get('decision', 'UNKNOWN')} — {roadmap.get('safety', {}).get('reason', '')}",
        "",
    ]
    questions = roadmap.get("clarification_questions", [])
    if questions:
        lines += ["## Clarification required", ""] + [f"- {q}" for q in questions] + [""]
    for phase in roadmap.get("phases", []):
        lines += [f"## {phase['name']}", "", phase.get("purpose", ""), ""]
        for task in phase.get("tasks", []):
            lines += [f"### {task['title']}", "", f"**Objective:** {task.get('objective', '')}", f"**Why it matters:** {task.get('why_it_matters', '')}", f"**Priority:** {task.get('priority', 'MEDIUM')}", "", "**Preconditions**"]
            lines += [f"- {x}" for x in task.get("preconditions", [])]
            lines += ["", f"**Expected evidence:** {task.get('expected_evidence', '')}", "", "**Steps"]
            for step in task.get("steps", []):
                lines += [f"- **{step['title']}** — {step.get('objective', '')} (evidence: {step.get('expected_evidence_type', '')}; completion: {step.get('completion_criteria', '')})"]
            lines += ["", "**False-positive checks"] + [f"- {x}" for x in task.get("false_positive_checks", [])]
            lines += ["", "**Stop conditions"] + [f"- {x}" for x in task.get("stop_conditions", [])]
            if task.get("citations"):
                lines += ["", "**Sources"] + [f"- {c.get('citation', c.get('locator', ''))} — {c.get('locator', '')}" for c in task["citations"]]
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
