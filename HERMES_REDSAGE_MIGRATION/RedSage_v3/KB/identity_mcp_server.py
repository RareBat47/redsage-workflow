"""Bounded MCP interface for internal identity/session assessment guidance."""
from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from KB.identity_retrieval_service import search_identity_kb

mcp = FastMCP("redsage-v3-identity-kb")

@mcp.tool()
def search_identity_session_kb(question: str, top_k: int = 8) -> str:
    """Return cited identity and session guidance; never authenticates or tests targets."""
    return json.dumps(search_identity_kb(question, top_k=top_k, actor_type="hermes"), indent=2)

if __name__ == "__main__":
    mcp.run()
