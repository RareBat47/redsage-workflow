"""Bounded MCP interface for internal RedSage workflow KB retrieval."""
from __future__ import annotations

import json
from mcp.server.fastmcp import FastMCP

from KB.workflow_retrieval_service import search_workflow_context

mcp = FastMCP("redsage-v3-workflow-kb")


@mcp.tool()
def search_workflow_kb(
    problem_statement: str,
    target_type: str = "web_app",
    environment_scope: str = "authorized_engagement",
    top_k: int = 8,
) -> str:
    """Return cited, policy-filtered workflow context; never executes tools or mutates projects."""
    result = search_workflow_context(
        problem_statement,
        environment_scope=environment_scope,
        top_k=top_k,
        actor_type="hermes",
    )
    result["target_type"] = target_type
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
