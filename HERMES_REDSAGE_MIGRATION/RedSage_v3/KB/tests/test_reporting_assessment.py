from KB.reporting_assessment import review_evidence


def test_review_evidence_keeps_insufficient_finding_as_draft():
    result = review_evidence({"title": "Test finding", "scope": "unlocked", "evidence": "", "reproduction": ""})
    assert result["finding_draft"]["status"] == "DRAFT"
    assert result["finding_draft"]["confirmation_allowed"] is False
