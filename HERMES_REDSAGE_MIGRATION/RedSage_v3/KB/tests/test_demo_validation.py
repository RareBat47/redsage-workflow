from pathlib import Path

from KB.demo_validation import validate_demo_document


DOC = Path(__file__).resolve().parents[1].parent / "docs" / "WORKFLOW_GENERATOR_DEMO.md"


def test_demo_document_has_required_safety_and_workflow_sections():
    result = validate_demo_document(DOC)
    assert result["passed"] is True
    assert result["missing"] == []


def test_demo_document_is_lab_bounded_and_not_real_target_authorization():
    text = DOC.read_text(encoding="utf-8").lower()
    assert "lab-only" in text
    assert "not authorization to test any real target" in text
    assert "stop conditions" in text
    assert "human approval" in text
