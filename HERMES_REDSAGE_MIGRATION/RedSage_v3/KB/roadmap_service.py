"""Internal roadmap generation facade: retrieve context, assemble, render."""
from __future__ import annotations
from typing import Any

from KB.workflow_retrieval_service import search_workflow_context
from KB.roadmap_assembler import assemble_roadmap
from KB.roadmap_renderer import render_markdown_roadmap


def generate_internal_roadmap(
    problem_statement: str,
    *,
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
    top_k: int = 8,
) -> dict[str, Any]:
    retrieval = search_workflow_context(
        problem_statement,
        environment_scope=environment_scope,
        top_k=top_k,
        actor_type="operator",
    )
    roadmap = assemble_roadmap(
        problem_statement,
        retrieval=retrieval,
        environment_scope=environment_scope,
        target_type=target_type,
    )
    return {
        "roadmap": roadmap,
        "markdown": render_markdown_roadmap(roadmap),
        "retrieval": retrieval,
    }
