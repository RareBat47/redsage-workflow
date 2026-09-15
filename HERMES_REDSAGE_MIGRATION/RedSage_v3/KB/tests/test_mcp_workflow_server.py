import json

from KB import mcp_workflow_server


def test_mcp_server_exposes_only_bounded_search_tool():
    tools = mcp_workflow_server.mcp._tool_manager._tools
    assert set(tools) == {"search_workflow_kb"}
    assert "execute" not in tools
    assert "approve" not in tools


def test_mcp_search_tool_returns_structured_result(monkeypatch):
    monkeypatch.setattr(
        mcp_workflow_server,
        "search_workflow_context",
        lambda *args, **kwargs: {"query_id": "q1", "citations": [], "warnings": []},
    )
    result = json.loads(mcp_workflow_server.search_workflow_kb("authorized web test"))
    assert result["query_id"] == "q1"
    assert result["target_type"] == "web_app"
