from KB.evaluation import load_cases, evaluate_case_output


def test_evaluation_cases_are_structured_and_cover_scope_gate():
    cases = load_cases()
    assert len(cases) >= 4
    assert any(case["id"] == "ambiguous_authorization" for case in cases)
    assert all(case["expected"]["must_include"] for case in cases)


def test_evaluate_case_output_reports_missing_requirements():
    result = evaluate_case_output(
        {"clarification_questions": [], "roadmap": "scope and evidence"},
        {"must_include": ["authorization", "stop condition"]},
    )
    assert result["passed"] is False
    assert "stop condition" in result["missing"]
