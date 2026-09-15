from KB.policies import filter_chunks_with_reasons


def test_policy_filter_returns_stable_reason_codes():
    allowed, reasons = filter_chunks_with_reasons([
        {"is_approved": False, "is_unsafe": False, "environment_scope": "authorized_engagement"},
        {"is_approved": True, "is_unsafe": True, "environment_scope": "authorized_engagement"},
        {"is_approved": True, "is_unsafe": False, "environment_scope": "unknown"},
    ])
    assert allowed == []
    assert reasons == ["not_approved", "unsafe", "unknown_scope"]
