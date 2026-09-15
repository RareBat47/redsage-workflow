import json

from KB import consolidated_mcp_server


def test_consolidated_mcp_exposes_only_roadmap_tool():
    assert set(consolidated_mcp_server.mcp._tool_manager._tools) == {"generate_internal_roadmap"}


def test_consolidated_mcp_returns_roadmap(monkeypatch):
    monkeypatch.setattr(
        consolidated_mcp_server,
        "generate_consolidated_internal_roadmap",
        lambda *args, **kwargs: {"roadmap": {"status": "NEEDS_CLARIFICATION"}, "markdown": "# Internal Workflow Roadmap"},
    )
    result = json.loads(consolidated_mcp_server.generate_internal_roadmap("Test this website"))
    assert result["roadmap"]["status"] == "NEEDS_CLARIFICATION"
    assert result["markdown"].startswith("# Internal Workflow Roadmap")
