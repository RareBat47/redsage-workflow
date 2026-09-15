from KB.citations import assemble_citations


def test_assemble_citations_includes_title_version_locator_and_notice():
    citations = assemble_citations([
        {
            "citation_id": "[1]",
            "chunk_id": "c1",
            "source_id": "s1",
            "source_version_id": "v1",
            "document_id": "d1",
            "title": "Authorization Guide",
            "locator": "09_scope_authorization/policy.md",
            "path": "09_scope_authorization/policy.md",
            "source_type": "redsage_policy",
            "trust_level": 5,
            "is_approved": True,
            "excerpt": "Confirm authorization before testing.",
            "score": 1.2,
            "content_hash": "a" * 64,
        }
    ])
    assert citations[0]["citation"] == "[1] Authorization Guide — redsage_policy, trust 5"
    assert citations[0]["locator"] == "09_scope_authorization/policy.md"
    assert citations[0]["excerpt"] == "Confirm authorization before testing."
    assert citations[0]["notice"] is None


def test_assemble_citations_marks_unapproved_source():
    result = assemble_citations([{"citation_id": "[1]", "title": "Draft", "source_type": "methodology", "trust_level": 3, "is_approved": False, "locator": "book", "excerpt": "text"}])
    assert "not approved" in result[0]["notice"]
