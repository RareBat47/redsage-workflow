from backend.services.cohere_service import clip_log, redact_sensitive_data

def test_clip_log():
    clipped = clip_log("\n".join(f"Line {i}" for i in range(120)), max_lines=80)
    assert "SNIPPED FOR BREVITY" in clipped
    assert len(clipped.splitlines()) == 81

def test_redact_secrets():
    redacted = redact_sensitive_data("User password='SecretPassword123' Bearer eyJhbGciOiJIUzI1Ni.test.token")
    assert "SecretPassword123" not in redacted
    assert "Bearer [REDACTED_TOKEN]" in redacted
    assert "[REDACTED_PASSWORD]" in redacted
