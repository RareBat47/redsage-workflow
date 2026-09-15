"""Create a review-only internal roadmap from policy-gated KB retrieval."""
from __future__ import annotations
from typing import Any

_CLARIFICATIONS = [
    "What exact hostnames or application instances are authorized?",
    "Who authorized the work and what is explicitly out of scope?",
    "What test accounts, data-handling rules, rate limits, and time limits apply?",
    "Is this a real authorized engagement or a lab/CTF environment?",
]

_PHASES = [
    ("Context, Authorization, and Scope", "Confirm the engagement boundary before technical work.", "Record authorization, in-scope assets, exclusions, limits, and stop conditions."),
    ("Application and Attack-Surface Understanding", "Establish the normal application flow and relevant assets.", "Document the authorized entry points, workflows, and baseline behavior."),
    ("Identity, Authentication, and Session Context", "Understand identity and session controls relevant to the problem.", "Capture a minimal authenticated baseline and applicable session context."),
    ("Authorization and Object-Access Context", "Assess whether protected resources are bound to the correct principal.", "Compare only authorized, controlled objects and record the minimum evidence."),
    ("Input, Output, and Data-Flow Analysis", "Identify relevant inputs, outputs, and server-side validation boundaries.", "Record observations and avoid broad or uncontrolled input exploration."),
    ("Business-Logic and Workflow Validation", "Validate the stated hypothesis in the approved workflow context.", "Repeat only the minimum controlled checks required to rule out false positives."),
    ("Evidence, Findings, and Reporting", "Preserve evidence and distinguish a hypothesis from a confirmed result.", "Capture sanitized evidence, citations, limitations, and remediation context."),
]


def _has_authorization(statement: str) -> bool:
    text = statement.lower()
    return any(token in text for token in ("authorized", "in scope", "permission", "training lab", "lab"))


def _phase(name: str, purpose: str, task: str, citations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "purpose": purpose,
        "status": "NOT_STARTED",
        "citation_count": len(citations),
        "tasks": [{
            "title": task,
            "objective": purpose,
            "why_it_matters": "Keeps the assessment evidence-led, authorized, and reproducible.",
            "priority": "HIGH" if name == "Context, Authorization, and Scope" else "MEDIUM",
            "preconditions": ["Scope and policy state must permit this task."],
            "expected_evidence": "Sanitized operator-collected notes or artifacts.",
            "false_positive_checks": ["Confirm the observed behavior belongs to the authorized target and context."],
            "stop_conditions": ["Stop and seek human clarification if scope, authorization, or evidence is ambiguous."],
            "steps": [{
                "title": task,
                "objective": purpose,
                "expected_evidence_type": "OPERATOR_NOTE",
                "completion_criteria": "The required observation is recorded with minimal sufficient evidence.",
            }],
            "citations": citations,
        }],
    }


def assemble_roadmap(
    problem_statement: str,
    *,
    retrieval: dict[str, Any],
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
) -> dict[str, Any]:
    if not problem_statement.strip():
        raise ValueError("problem_statement is required")
    classification = retrieval.get("query_classification", {"primary": "general_workflow"})
    citations = list(retrieval.get("citations", []))
    lab = environment_scope == "lab_only" or classification.get("primary") == "lab"
    authorized = _has_authorization(problem_statement)
    if not authorized:
        return {
            "status": "NEEDS_CLARIFICATION",
            "target_type": target_type,
            "environment_scope": environment_scope,
            "receipt_id": retrieval.get("query_id"),
            "query_classification": classification,
            "safety": {"decision": "BLOCKED", "reason": "Authorization and scope are not explicit."},
            "clarification_questions": _CLARIFICATIONS,
            "phases": [],
            "citations": citations,
            "warnings": retrieval.get("warnings", []),
        }
    safety = {
        "decision": "LAB_ONLY" if lab else "READY_FOR_INTERNAL_REVIEW",
        "reason": "Lab context must not be transferred to a real target." if lab else "Draft is review-only and must be explicitly applied.",
    }
    return {
        "status": "READY_FOR_REVIEW",
        "target_type": target_type,
        "environment_scope": "lab_only" if lab else environment_scope,
        "receipt_id": retrieval.get("query_id"),
        "query_classification": classification,
        "safety": safety,
        "clarification_questions": [],
        "phases": [_phase(name, purpose, task, citations) for name, purpose, task in _PHASES],
        "citations": citations,
        "warnings": retrieval.get("warnings", []),
    }
