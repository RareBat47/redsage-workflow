from KB.engagement_workflow import run_internal_engagement_workflow


def test_engagement_workflow_returns_roadmap_and_guidance(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "KB.engagement_workflow.generate_consolidated_internal_roadmap",
        lambda *args, **kwargs: {
            "roadmap": {"status": "READY_FOR_REVIEW", "phases": [], "receipt_id": "roadmap-q"},
            "markdown": "# Internal Workflow Roadmap",
            "retrieval": {"citations": [], "query_id": "roadmap-q"},
        },
    )
    monkeypatch.setattr(
        "KB.engagement_workflow.search_assessment_kb",
        lambda *args, **kwargs: {
            "citations": [{"citation": "[1] Assessment", "assessment_phase": "authorization"}],
            "query_id": "assessment-q",
        },
    )
    result = run_internal_engagement_workflow(
        "Authorized web application access-control assessment",
        selected_step="Check object-level authorization",
        receipt_directory=tmp_path,
    )
    assert result["roadmap"]["status"] == "READY_FOR_REVIEW"
    assert result["step_guidance"]["query_id"] == "assessment-q"
    assert result["workflow_status"] == "READY_FOR_REVIEW"


def test_engagement_workflow_blocks_evidence_without_authorized_scope():
    result = run_internal_engagement_workflow(
        "Test this website",
        evidence={"title": "Possible issue", "scope": "unlocked", "evidence": "data", "reproduction": "steps"},
    )
    assert result["workflow_status"] == "NEEDS_CLARIFICATION"
    assert result["evidence_review"]["finding_draft"]["confirmation_allowed"] is False
