"""Bounded MCP interface for internal Web Application assessment guidance."""
from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from KB.assessment_retrieval_service import search_assessment_kb

mcp = FastMCP("redsage-v3-assessment-web-kb")

@mcp.tool()
def search_assessment_kb_tool(
    assessment_question: str,
    environment_scope: str = "authorized_engagement",
    top_k: int = 8,
) -> str:
    """Return cited assessment guidance and evidence expectations; never executes tools."""
    result = search_assessment_kb(
        assessment_question,
        environment_scope=environment_scope,
        top_k=top_k,
        actor_type="hermes",
    )
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()
