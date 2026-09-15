from KB.policies import policy_decision


def test_missing_safety_metadata_is_denied_for_engagements():
    allowed, reason = policy_decision({}, environment_scope="authorized_engagement")
    assert allowed is False
    assert reason in {"not_approved", "unsafe", "unknown_scope"}


def test_missing_scope_is_denied_even_when_other_flags_exist():
    allowed, reason = policy_decision(
        {"is_approved": True, "is_unsafe": False},
        environment_scope="authorized_engagement",
    )
    assert allowed is False
    assert reason == "unknown_scope"
