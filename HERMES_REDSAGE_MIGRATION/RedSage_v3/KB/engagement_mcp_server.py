"""Bounded MCP interface for the internal RedSage engagement workflow."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from KB.engagement_workflow import run_internal_engagement_workflow as _run_engagement_workflow

mcp = FastMCP("redsage-v3-engagement-workflow")


@mcp.tool()
def generate_engagement_workflow(
    problem_statement: str,
    selected_step: str | None = None,
    evidence_title: str | None = None,
    scope_status: str | None = None,
    evidence_summary: str | None = None,
    reproduction_summary: str | None = None,
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
    top_k: int = 8,
) -> str:
    """Create a review-only roadmap, step guidance, and draft evidence review; never executes tools, changes scope, or confirms findings."""
    evidence = None
    if any(value is not None for value in (evidence_title, scope_status, evidence_summary, reproduction_summary)):
        evidence = {
            "title": evidence_title or "Untitled finding",
            "scope": scope_status or "unlocked",
            "evidence": evidence_summary or "",
            "reproduction": reproduction_summary or "",
        }
    result = _run_engagement_workflow(
        problem_statement,
        selected_step=selected_step,
        evidence=evidence,
        environment_scope=environment_scope,
        target_type=target_type,
        top_k=top_k,
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()