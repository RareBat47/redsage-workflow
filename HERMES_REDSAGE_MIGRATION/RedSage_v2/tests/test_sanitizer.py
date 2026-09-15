from backend.services.cohere_service import create_safe_excerpt, redact_sensitive_data


def test_redaction_covers_cli_encoded_and_multiline_secrets():
    raw = (
        '--password "cli-secret" -p second-secret\n'
        '-H "Authorization: Bearer header-secret"\n'
        'password: "json-secret"\n'
        'token=%65%79%4aencoded-secret\n'
        'Authorization: Basic dXNlcjpwYXNz\n'
    )
    clean = redact_sensitive_data(raw)
    for secret in ("cli-secret", "second-secret", "header-secret", "json-secret", "encoded-secret", "dXNlcjpwYXNz"):
        assert secret not in clean


def test_excerpt_redacts_before_boundary_clipping():
    raw = "safe-head " + ("x" * 780) + ' password="boundary-secret" safe-tail'
    excerpt = create_safe_excerpt(raw, max_chars=200)
    assert len(excerpt) <= 200
    assert "boundary-secret" not in excerpt
    assert "[REDACTED_PASSWORD]" in excerpt or "SNIPPED" in excerpt
