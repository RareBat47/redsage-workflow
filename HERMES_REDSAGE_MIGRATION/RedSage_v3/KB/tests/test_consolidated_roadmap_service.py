from KB.consolidated_roadmap_service import generate_consolidated_internal_roadmap


def test_consolidated_roadmap_uses_all_relevant_domains(monkeypatch):
    def fake_search(query, **kwargs):
        assert len(kwargs["profiles"]) == 6
        return {
            "query_id": "q-consolidated",
            "query_classification": {"primary": "authentication"},
            "citations": [{"citation": "[1] Identity", "locator": "identity.md", "kb_domain": "identity"}],
            "warnings": [], "candidate_count": 10, "filtered_count": 0,
        }

    monkeypatch.setattr("KB.consolidated_roadmap_service.search_consolidated", fake_search)
    result = generate_consolidated_internal_roadmap("Authorized web application login assessment")
    assert result["roadmap"]["status"] == "READY_FOR_REVIEW"
    assert result["roadmap"]["receipt_id"] == "q-consolidated"
    assert result["roadmap"]["retrieval_domains"] == ["identity"]
    assert "[1] Identity" in result["markdown"]


def test_consolidated_roadmap_preserves_clarification_gate(monkeypatch):
    monkeypatch.setattr(
        "KB.consolidated_roadmap_service.search_consolidated",
        lambda *args, **kwargs: {
            "query_id": "q-blocked", "query_classification": {"primary": "general_workflow"},
            "citations": [], "warnings": [],
        },
    )
    result = generate_consolidated_internal_roadmap("Test this website")
    assert result["roadmap"]["status"] == "NEEDS_CLARIFICATION"
    assert result["roadmap"]["safety"]["decision"] == "BLOCKED"
    assert result["retrieval"]["skipped"] == "authorization_clarification_required"
    assert result["markdown"].startswith("# Internal Workflow Roadmap")
