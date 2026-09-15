import json

from KB import engagement_mcp_server


def test_engagement_mcp_exposes_only_the_workflow_tool():
    assert set(engagement_mcp_server.mcp._tool_manager._tools) == {"generate_engagement_workflow"}


def test_engagement_mcp_delegates_once_to_the_underlying_workflow(monkeypatch):
    calls = []

    def fake(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return {"workflow_status": "READY_FOR_REVIEW", "roadmap": {}, "markdown": "# Internal Workflow Roadmap"}

    monkeypatch.setattr(engagement_mcp_server, "_run_engagement_workflow", fake)
    result = json.loads(engagement_mcp_server.generate_engagement_workflow("Authorized web assessment"))

    assert len(calls) == 1
    assert calls[0]["kwargs"]["evidence"] is None
    assert result["workflow_status"] == "READY_FOR_REVIEW"


def test_engagement_mcp_builds_evidence_payload_only_when_fields_are_supplied(monkeypatch):
    captured = {}

    def fake(*args, **kwargs):
        captured.update(kwargs)
        return {"workflow_status": "NEEDS_CLARIFICATION"}

    monkeypatch.setattr(engagement_mcp_server, "_run_engagement_workflow", fake)
    engagement_mcp_server.generate_engagement_workflow(
        "Authorized web assessment",
        evidence_title="Possible IDOR",
        scope_status="unlocked",
        evidence_summary="sanitized excerpt",
        reproduction_summary="controlled comparison",
    )

    assert captured["evidence"] == {
        "title": "Possible IDOR",
        "scope": "unlocked",
        "evidence": "sanitized excerpt",
        "reproduction": "controlled comparison",
    }