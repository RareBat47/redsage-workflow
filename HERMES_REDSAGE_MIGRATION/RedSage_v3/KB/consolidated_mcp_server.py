"""Bounded MCP interface for consolidated internal roadmap generation."""
from __future__ import annotations

import json
from mcp.server.fastmcp import FastMCP

from KB.consolidated_roadmap_service import generate_consolidated_internal_roadmap

mcp = FastMCP("redsage-v3-consolidated-roadmap")


@mcp.tool()
def generate_internal_roadmap(
    problem_statement: str,
    environment_scope: str = "authorized_engagement",
    target_type: str = "web_app",
    top_k: int = 8,
) -> str:
    """Generate a cited, review-only roadmap; never executes tools or changes scope."""
    result = generate_consolidated_internal_roadmap(
        problem_statement,
        environment_scope=environment_scope,
        target_type=target_type,
        top_k=top_k,
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
