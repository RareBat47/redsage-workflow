from KB.retrieval import rank_chunks


def test_rank_chunks_combines_vector_lexical_trust_and_lab_penalty():
    candidates = [
        {"chunk_id":"safe", "text":"authorization scope evidence", "vector_score":0.7, "source_type":"owasp", "trust_level":4, "environment_scope":"authorized_engagement"},
        {"chunk_id":"lab", "text":"authorization scope evidence", "vector_score":0.8, "source_type":"lab", "trust_level":3, "environment_scope":"lab_only"},
    ]
    ranked = rank_chunks("authorization scope evidence", candidates)
    assert ranked[0]["chunk_id"] == "safe"
    assert "score_components" in ranked[0]
