"""Active target selection tests for the tasks endpoint."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _multi_target_project():
    project = client.post("/api/v1/projects", json={"name": "Multi Target Test"}).json()
    project_id = project["id"]
    client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={
            "in_scope_whitelist": ["alpha.local", "beta.local"],
            "out_of_scope_blacklist": ["gamma.local"],
            "max_rate_limit": 25,
        },
    )
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


def test_default_target_is_first_whitelist_entry():
    project_id = _multi_target_project()
    command, safe = _first_command(project_id)
    assert "alpha.local" in command
    assert "beta.local" not in command
    assert safe is True


def test_selected_target_changes_resolved_command():
    project_id = _multi_target_project()
    command, safe = _first_command(project_id, "?target_host=beta.local")
    assert "beta.local" in command
    assert "alpha.local" not in command
    assert "25" in command, "Rate limit must still be resolved from scope"
    assert safe is True


def test_target_outside_whitelist_is_rejected():
    project_id = _multi_target_project()
    response = client.get(f"/api/v1/projects/{project_id}/tasks?target_host=gamma.local")
    assert response.status_code == 422
    assert "whitelist" in response.json()["detail"].lower()
    response = client.get(f"/api/v1/projects/{project_id}/tasks?target_host=evil.example.com")
    assert response.status_code == 422


def test_scope_safety_follows_selected_target():
    project_id = _multi_target_project()
    # Blacklist the currently selected target via direct scope rewrite is not
    # possible after locking, so verify the safety computation itself through
    # the validator used by the endpoint.
    from backend.services.scope_validator import is_target_in_scope

    whitelist = ["alpha.local", "beta.local"]
    blacklist = ["beta.local"]
    assert is_target_in_scope("beta.local", whitelist, blacklist) is False
    assert is_target_in_scope("alpha.local", whitelist, blacklist) is True
