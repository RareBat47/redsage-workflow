from KB.retrieval import classify_query, rank_chunks


def test_classify_query_prioritizes_scope_when_authorization_is_ambiguous():
    result = classify_query("Authorization is unclear and the target scope is not confirmed")
    assert result["primary"] == "authorization_scope"


def test_rank_chunks_prioritizes_scope_policy_over_technical_content():
    candidates = [
        {"chunk_id": "technical", "text": "authentication testing", "vector_score": 0.95, "source_type": "owasp", "trust_level": 4},
        {"chunk_id": "policy", "text": "pause when authorization or scope is unclear", "vector_score": 0.70, "source_type": "redsage_policy", "trust_level": 5},
    ]
    ranked = rank_chunks("authorization scope unclear", candidates)
    assert ranked[0]["chunk_id"] == "policy"
    assert ranked[0]["score_components"]["policy"] > 0
