"""FastMCP stdio server exposing the RedSage KB to OpenCode and other AI agents.

Run from the project root:
    python -m interfaces.mcp_server

OpenCode example (~/.config/opencode/opencode.json):
    {
      "mcp": {
        "redsage-kb": {
          "type": "local",
          "command": ["python", "-m", "interfaces.mcp_server"],
          "cwd": "D:/HIGH LEVELS OF WORKS/RedSage_v2",
          "enabled": true
        }
      }
    }
"""

import json

from mcp.server.fastmcp import FastMCP

from core.kb_engine import KBEngine

mcp = FastMCP("redsage-kb")
engine = KBEngine()


@mcp.tool()
def kb_search(query: str, top_k: int = 5) -> str:
    """Search the RedSage security knowledge base and return scored citations."""
    citations = engine.search(query, top_k=top_k)
    return json.dumps(
        [
            {
                "chunk_id": citation.chunk_id,
                "title": citation.title,
                "source": citation.source,
                "url": citation.url,
                "score": round(citation.score, 4),
                "text": citation.text,
            }
            for citation in citations
        ],
        indent=2,
    )


@mcp.tool()
def kb_sources() -> str:
    """List registered KB sources with document and chunk counts."""
    return json.dumps(engine.list_sources(), indent=2)


@mcp.tool()
def kb_stats() -> str:
    """List all ChromaDB collections with item counts."""
    return json.dumps(engine.collection_stats(), indent=2)


if __name__ == "__main__":
    mcp.run()
