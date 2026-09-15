from KB.roadmap_service import generate_internal_roadmap


def test_roadmap_service_uses_retrieval_then_returns_structured_and_rendered_draft(monkeypatch):
    monkeypatch.setattr(
        "KB.roadmap_service.search_workflow_context",
        lambda *args, **kwargs: {
            "query_id": "q1",
            "query_classification": {"primary": "authentication"},
            "citations": [],
            "warnings": [],
        },
    )
    result = generate_internal_roadmap("Authorized web application assessment of login behavior")
    assert result["roadmap"]["status"] == "READY_FOR_REVIEW"
    assert result["roadmap"]["receipt_id"] == "q1"
    assert "# Internal Workflow Roadmap" in result["markdown"]


def test_roadmap_service_returns_clarification_draft_without_active_workflow_mutation(monkeypatch):
    monkeypatch.setattr(
        "KB.roadmap_service.search_workflow_context",
        lambda *args, **kwargs: {"query_id": "q2", "query_classification": {"primary": "general_workflow"}, "citations": [], "warnings": []},
    )
    result = generate_internal_roadmap("Test this website")
    assert result["roadmap"]["status"] == "NEEDS_CLARIFICATION"
    assert "## Clarification required" in result["markdown"]
