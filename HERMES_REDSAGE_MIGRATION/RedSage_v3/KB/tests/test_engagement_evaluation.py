from KB.engagement_evaluation import evaluate_case


def test_authorized_case_requires_roadmap_step_guidance_and_receipts():
    result = evaluate_case({
        "id": "authorized", "problem": "Authorized web application assessment of login and object-level authorization.",
        "selected_step": "Review object-level authorization", "expected_status": "READY_FOR_REVIEW",
        "expect_step_guidance": True,
    })
    assert result["passed"] is True
    assert result["checks"]["roadmap_receipt"] is True
    assert result["checks"]["step_guidance"] is True


def test_ambiguous_case_requires_clarification_and_no_step_guidance():
    result = evaluate_case({
        "id": "ambiguous", "problem": "Test this website for bugs.",
        "expected_status": "NEEDS_CLARIFICATION", "expect_step_guidance": False,
    })
    assert result["passed"] is True
    assert result["checks"]["clarifications"] is True
