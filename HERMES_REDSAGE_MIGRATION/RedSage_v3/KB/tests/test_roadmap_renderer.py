from KB.roadmap_renderer import render_markdown_roadmap


def test_renderer_shows_safety_receipt_phases_and_citations():
    roadmap = {
        "status": "READY_FOR_REVIEW",
        "target_type": "web_app",
        "environment_scope": "authorized_engagement",
        "receipt_id": "q1",
        "safety": {"decision": "READY_FOR_INTERNAL_REVIEW", "reason": "Review first."},
        "query_classification": {"primary": "authentication"},
        "phases": [{"name": "Phase 1", "purpose": "Context", "status": "NOT_STARTED", "tasks": [{"title": "Confirm scope", "objective": "Scope", "why_it_matters": "Safety", "priority": "HIGH", "preconditions": ["Authorization"], "expected_evidence": "Notes", "false_positive_checks": ["Check"], "stop_conditions": ["Stop"], "steps": [{"title": "Record", "objective": "Record", "expected_evidence_type": "OPERATOR_NOTE", "completion_criteria": "Saved"}], "citations": [{"citation": "[1] Scope", "locator": "scope.md"}]}]}],
        "citations": [],
        "warnings": [],
    }
    rendered = render_markdown_roadmap(roadmap)
    assert "READY_FOR_INTERNAL_REVIEW" in rendered
    assert "Receipt: q1" in rendered
    assert "## Phase 1" in rendered
    assert "[1] Scope" in rendered
    assert "Stop conditions" in rendered
