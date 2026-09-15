"""Bounded MCP interface for internal evidence/reporting guidance."""
from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from KB.reporting_assessment import search_reporting_context, review_evidence

mcp = FastMCP("redsage-v3-evidence-reporting-kb")

@mcp.tool()
def search_evidence_reporting_kb(question: str, top_k: int = 8) -> str:
    """Return cited reporting guidance; never confirms findings or sends reports."""
    return json.dumps(search_reporting_context(question, top_k=top_k, actor_type="hermes"), indent=2)

@mcp.tool()
def assess_evidence_for_draft(title: str, scope: str, evidence: str, reproduction: str) -> str:
    """Assess evidence completeness and return a draft-only finding record."""
    return json.dumps(review_evidence({"title": title, "scope": scope, "evidence": evidence, "reproduction": reproduction}), indent=2)

if __name__ == "__main__":
    mcp.run()
