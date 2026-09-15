from KB.evidence_reporting_retrieval import search_reporting_guidance


def test_reporting_retrieval_marks_domain_and_preserves_result(monkeypatch):
    monkeypatch.setattr(
        "KB.evidence_reporting_retrieval.search_assessment_kb",
        lambda query, **kwargs: {"query": query, "citations": [], "query_id": "q1"},
    )
    result = search_reporting_guidance("access control observation")
    assert result["kb_domain"] == "evidence_findings_reporting"
    assert "evidence" in result["query"]
