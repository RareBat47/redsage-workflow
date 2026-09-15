from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def make_locked_project(name: str):
    project = client.post("/api/v1/projects", json={"name": name}).json()
    project_id = project["id"]
    client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["target.local"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    client.post(f"/api/v1/projects/{project_id}/scope/lock")
    return project_id


def first_task(project_id: str):
    return client.get(f"/api/v1/projects/{project_id}/tasks").json()[0]["tasks"][0]


def test_digest_coverage_matches_report_readiness_exactly(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id = make_locked_project("Digest Parity Test")
    task = first_task(project_id)

    readiness = client.get(f"/api/v1/projects/{project_id}/report/readiness").json()
    digest = client.get(f"/api/v1/projects/{project_id}/workflow/digest").json()
    assert digest["coverage"] == readiness["coverage"]

    client.post(f"/api/v1/projects/{project_id}/tasks/{task['id']}/state", json={"status": "COMPLETED"})
    readiness_after = client.get(f"/api/v1/projects/{project_id}/report/readiness").json()
    digest_after = client.get(f"/api/v1/projects/{project_id}/workflow/digest").json()
    assert digest_after["coverage"] == readiness_after["coverage"]


def test_digest_reports_assets_findings_and_evidence_counts(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id = make_locked_project("Digest Counts Test")
    task = first_task(project_id)
    verify = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/verify",
        json={"raw_content": "review complete https://target.local/backup.zip"},
    )
    assert verify.status_code == 200
    evidence_id = verify.json()["evidence_id"]

    drafted = client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Confirmed exposure", "evidence_id": evidence_id, "severity": "HIGH"},
    )
    assert drafted.status_code == 200
    finding_id = drafted.json()["finding_id"]
    confirmed = client.post(
        f"/api/v1/projects/{project_id}/findings/{finding_id}/confirm",
        json={
            "evidence_id": evidence_id,
            "description": "An exposed archive was observed in the captured evidence.",
            "remediation": "Remove the exposed archive.",
            "reproduction_steps": "Reviewed captured evidence.",
        },
    )
    assert confirmed.status_code == 200

    digest = client.get(f"/api/v1/projects/{project_id}/workflow/digest").json()
    assert digest["evidence_count"] == 1
    assert digest["asset_count"] >= 1
    assert digest["confirmed_finding_count"] == 1
    assert len(digest["phases"]) == 7


def test_boss_mentor_offline_fallback_persists_project_scope_only(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id = make_locked_project("Boss Mentor Test")
    task = first_task(project_id)

    response = client.post(
        f"/api/v1/projects/{project_id}/mentor/boss",
        json={"mode": "summarize", "user_message": "What is my current status?"},
    )
    assert response.status_code == 200
    assert response.json()["ai_available"] is False

    history = client.get(f"/api/v1/projects/{project_id}/mentor/boss/history").json()
    assert [row["role"] for row in history] == ["user", "assistant"]
    assert history[0]["content"] == "What is my current status?"

    task_history = client.get(f"/api/v1/projects/{project_id}/tasks/{task['id']}/mentor/history").json()
    assert task_history == []


def test_boss_mentor_provider_failure_never_returns_500(monkeypatch):
    import cohere as cohere_module

    class Down:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            raise RuntimeError("provider unavailable")

    monkeypatch.setenv("CO_API_KEY", "configured-but-down")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", Down)
    project_id = make_locked_project("Boss Mentor Failure Test")
    response = client.post(
        f"/api/v1/projects/{project_id}/mentor/boss",
        json={"mode": "summarize", "user_message": "Am I ready to report?"},
    )
    assert response.status_code == 200
    assert response.json()["ai_available"] is False


def test_digest_route_rejects_unknown_project():
    response = client.get("/api/v1/projects/not-a-real-project/workflow/digest")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
