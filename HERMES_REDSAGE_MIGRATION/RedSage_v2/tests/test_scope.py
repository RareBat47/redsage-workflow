from backend.services.scope_validator import is_target_in_scope, is_valid_target

def test_target_validation():
    assert is_valid_target("target.local")
    assert is_valid_target("192.168.1.1")
    assert is_valid_target("10.0.0.0/24")
    assert not is_valid_target("invalid!domain@")

def test_scope_checks():
    assert is_target_in_scope("target.local", ["target.local"], [])
    assert not is_target_in_scope("admin.target.local", ["target.local"], ["admin.target.local"])
