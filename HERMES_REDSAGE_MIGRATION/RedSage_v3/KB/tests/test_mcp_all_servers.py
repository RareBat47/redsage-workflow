import json

from KB import api_mcp_server, identity_mcp_server, reporting_mcp_server


def test_api_mcp_has_only_bounded_search_tool():
    assert set(api_mcp_server.mcp._tool_manager._tools) == {"search_api_assessment_kb"}


def test_identity_mcp_has_only_bounded_search_tool():
    assert set(identity_mcp_server.mcp._tool_manager._tools) == {"search_identity_session_kb"}


def test_reporting_mcp_has_only_search_and_draft_assessment_tools():
    assert set(reporting_mcp_server.mcp._tool_manager._tools) == {
        "search_evidence_reporting_kb",
        "assess_evidence_for_draft",
    }
