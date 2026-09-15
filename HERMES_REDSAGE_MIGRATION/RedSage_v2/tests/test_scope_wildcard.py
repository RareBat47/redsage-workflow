"""Wildcard-domain and CIDR scope support tests.

Covers the validator, the entry-matching rules, and the API surface (scope
update, task command resolution, mentor scope gate). These tests never touch
the evidence pipeline, so no on-disk artifacts are created.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.scope_validator import (
    is_target_in_scope,
    is_target_whitelisted,
    is_valid_target,
    target_matches_scope_entry,
)

client = TestClient(app)


def test_wildcard_entries_are_valid_targets():
    assert is_valid_target("*.example.com")
    assert is_valid_target("*.EXAMPLE.com")
    assert is_valid_target("*.a.b-example.com")
    assert not is_valid_target("*")
    assert not is_valid_target("*.")
    assert not is_valid_target("*example.com")
    assert not is_valid_target("api.*.example.com")
    assert not is_valid_target("*.com")


def test_wildcard_matching_covers_apex_and_subdomains():
    assert target_matches_scope_entry("example.com", "*.example.com")
    assert target_matches_scope_entry("api.example.com", "*.example.com")
    assert target_matches_scope_entry("a.b.example.com", "*.example.com")
    assert target_matches_scope_entry("API.Example.COM.", "*.example.COM")


def test_wildcard_matching_enforces_label_boundaries():
    assert not target_matches_scope_entry("evil-example.com", "*.example.com")
    assert not target_matches_scope_entry("example.com.evil.com", "*.example.com")
    assert not target_matches_scope_entry("notexample.com", "*.example.com")


def test_bare_domain_stays_exact_only():
    assert not target_matches_scope_entry("api.example.com", "example.com")
    assert target_matches_scope_entry("example.com", "example.com")


def test_wildcard_target_is_not_a_concrete_host():
    assert not target_matches_scope_entry("*.example.com", "*.example.com")
    assert not is_target_whitelisted("*.example.com", ["*.example.com"])


def test_cidr_entries_match_member_addresses():
    assert target_matches_scope_entry("10.1.2.3", "10.0.0.0/8")
    assert not target_matches_scope_entry("11.0.0.1", "10.0.0.0/8")
    assert target_matches_scope_entry("192.168.1.1", "192.168.1.1")  # bare IP = /32
    assert not target_matches_scope_entry("192.168.1.2", "192.168.1.1")


def test_blacklist_carves_out_of_wildcard_scope():
    whitelist = ["*.example.com"]
    assert not is_target_in_scope("internal.example.com", whitelist, ["internal.example.com"])
    assert not is_target_in_scope("db.internal.example.com", whitelist, ["*.internal.example.com"])
    assert not is_target_in_scope("10.9.9.9", ["10.0.0.0/8"], ["10.9.0.0/16"])
    assert is_target_in_scope("api.example.com", whitelist, ["internal.example.com"])


def _wildcard_project() -> str:
    project = client.post("/api/v1/projects", json={"name": "Wildcard Scope Test"}).json()
    project_id = project["id"]
    response = client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={
            "in_scope_whitelist": ["*.example.com"],
            "out_of_scope_blacklist": ["internal.example.com"],
            "max_rate_limit": 10,
        },
    )
    assert response.status_code == 200
    client.post(f"/api/v1/projects/{project_id}/scope/lock")
    return project_id


def _first_command(project_id: str, query: str = "") -> tuple[str, bool]:
    phases = client.get(f"/api/v1/projects/{project_id}/tasks{query}").json()
    task = next(
        task
        for phase in phases
        for task in phase["tasks"]
        if task["resolved_command"]
    )
    return task["resolved_command"], task["is_scope_safe"]


def test_scope_update_accepts_wildcard_and_rejects_bad_wildcards():
    project = client.post("/api/v1/projects", json={"name": "Wildcard Validation"}).json()
    project_id = project["id"]
    ok = client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["*.example.com"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    assert ok.status_code == 200
    bad = client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["*example.com"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    assert bad.status_code == 422


def test_tasks_resolve_for_hosts_covered_by_wildcard():
    project_id = _wildcard_project()
    command, safe = _first_command(project_id, "?target_host=api.example.com")
    assert "api.example.com" in command
    assert safe is True


def test_tasks_reject_hosts_outside_wildcard():
    project_id = _wildcard_project()
    assert client.get(f"/api/v1/projects/{project_id}/tasks?target_host=evil-example.com").status_code == 422
    assert client.get(f"/api/v1/projects/{project_id}/tasks?target_host=other.org").status_code == 422
    # Blacklisted even though covered by the wildcard: resolves, but unsafe.
    command, safe = _first_command(project_id, "?target_host=internal.example.com")
    assert "internal.example.com" in command
    assert safe is False


def test_wildcard_only_scope_has_no_default_target():
    project_id = _wildcard_project()
    command, safe = _first_command(project_id)
    assert "TARGET_UNSPECIFIED" in command
    assert safe is False


def test_mixed_scope_defaults_to_first_concrete_entry():
    project = client.post("/api/v1/projects", json={"name": "Mixed Scope"}).json()
    project_id = project["id"]
    client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["*.example.com", "alpha.example.com"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    client.post(f"/api/v1/projects/{project_id}/scope/lock")
    command, safe = _first_command(project_id)
    assert "alpha.example.com" in command
    assert safe is True


def test_mentor_accepts_host_covered_by_wildcard(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id = _wildcard_project()
    task = client.get(f"/api/v1/projects/{project_id}/tasks?target_host=api.example.com").json()[0]["tasks"][0]
    ok = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/mentor",
        json={"mode": "teach", "user_message": "Explain this task", "target_host": "api.example.com"},
    )
    assert ok.status_code == 200
    rejected = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/mentor",
        json={"mode": "teach", "user_message": "Explain this task", "target_host": "other.org"},
    )
    assert rejected.status_code == 422

