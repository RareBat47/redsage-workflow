from KB.reporting_logic import classify_evidence_strength, build_finding_record


def test_evidence_strength_requires_minimum_fields():
    result = classify_evidence_strength({"evidence": "request and response", "scope": "locked", "reproduction": "steps"})
    assert result["status"] == "READY_FOR_REVIEW"
    assert result["missing"] == []


def test_finding_record_stays_draft_without_sufficient_evidence():
    result = build_finding_record("Access control issue", {"evidence": "", "scope": "unlocked", "reproduction": ""})
    assert result["status"] == "DRAFT"
    assert result["confirmation_allowed"] is False
    assert "scope" in result["missing"]
