"""Bounded MCP interface for internal API assessment guidance."""
from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from KB.api_retrieval_service import search_api_kb

mcp = FastMCP("redsage-v3-api-kb")

@mcp.tool()
def search_api_assessment_kb(question: str, top_k: int = 8) -> str:
    """Return cited API assessment guidance; never executes tools or accesses targets."""
    return json.dumps(search_api_kb(question, top_k=top_k, actor_type="hermes"), indent=2)

if __name__ == "__main__":
    mcp.run()
