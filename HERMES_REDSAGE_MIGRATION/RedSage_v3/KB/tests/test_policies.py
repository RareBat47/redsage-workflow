from KB.policies import filter_chunks


def test_real_engagement_excludes_lab_and_unapproved_chunks():
    chunks = [
        {"chunk_id": "safe", "source_type": "owasp", "is_approved": True, "is_unsafe": False, "environment_scope": "authorized_engagement"},
        {"chunk_id": "lab", "source_type": "lab", "is_approved": True, "is_unsafe": False, "environment_scope": "lab_only"},
        {"chunk_id": "draft", "source_type": "book", "is_approved": False, "is_unsafe": False, "environment_scope": "authorized_engagement"},
    ]
    assert [c["chunk_id"] for c in filter_chunks(chunks, environment_scope="authorized_engagement")] == ["safe"]


def test_lab_scope_allows_lab_chunks():
    chunks = [{"chunk_id": "lab", "source_type": "lab", "is_approved": True, "is_unsafe": False, "environment_scope": "lab_only"}]
    assert [c["chunk_id"] for c in filter_chunks(chunks, environment_scope="lab_only")] == ["lab"]
