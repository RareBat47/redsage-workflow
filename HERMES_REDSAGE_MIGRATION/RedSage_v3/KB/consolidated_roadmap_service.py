"""Internal roadmap generation using the consolidated multi-KB retrieval path."""
from __future__ import annotations
from typing import Any
from KB.consolidated_retrieval import KBProfile, search_consolidated
from KB.roadmap_assembler import assemble_roadmap
from KB.roadmap_renderer import render_markdown_roadmap

PROFILES = (
    KBProfile("redsage_v3_workflow_cohere_v1", "workflow", "workflow-v1"),
    KBProfile("redsage_v3_assessment_web_cohere_v1", "assessment", "assessment-v1"),
    KBProfile("redsage_v3_evidence_reporting_cohere_v1", "reporting", "reporting-v1"),
    KBProfile("redsage_v3_assessment_identity_cohere_v1", "identity", "identity-v1"),
    KBProfile("redsage_v3_assessment_authorization_cohere_v1", "authorization", "authorization-v1"),
    KBProfile("redsage_v3_assessment_api_cohere_v1", "api", "api-v1"),
)


def generate_consolidated_internal_roadmap(
    problem_statement: str,
    *,
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
    top_k: int = 8,
    profiles: tuple[KBProfile, ...] = PROFILES,
    **retrieval_kwargs: Any,
) -> dict[str, Any]:
    retrieval_options = dict(retrieval_kwargs)
    retrieval_options.setdefault("actor_type", "operator")
    # Enforce the clarification gate before any provider/vector call. An
    # ambiguous statement must not trigger retrieval or spend Cohere credits.
    preliminary = assemble_roadmap(
        problem_statement,
        retrieval={"query_id": None, "query_classification": {"primary": "general_workflow"}, "citations": [], "warnings": []},
        environment_scope=environment_scope,
        target_type=target_type,
    )
    if preliminary["status"] == "NEEDS_CLARIFICATION":
        return {"roadmap": preliminary, "markdown": render_markdown_roadmap(preliminary), "retrieval": {"query_id": None, "citations": [], "warnings": [], "skipped": "authorization_clarification_required"}}
    retrieval = search_consolidated(
        problem_statement,
        profiles=profiles,
        environment_scope=environment_scope,
        top_k=top_k,
        **retrieval_options,
    )
    roadmap = assemble_roadmap(
        problem_statement,
        retrieval=retrieval,
        environment_scope=environment_scope,
        target_type=target_type,
    )
    roadmap["retrieval_domains"] = retrieval.get("kb_domains") or sorted({item.get("kb_domain") for item in retrieval.get("citations", []) if item.get("kb_domain")})
    return {"roadmap": roadmap, "markdown": render_markdown_roadmap(roadmap), "retrieval": retrieval}
