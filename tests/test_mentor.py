"""Task AI mentor endpoint tests: schema, context pack, and Cohere fallbacks."""

import json
import os
from types import SimpleNamespace

import cohere as cohere_module
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class _FakeCohereOk:
    prompts = []

    def __init__(self, *args, **kwargs):
        pass

    def chat(self, *args, **kwargs):
        _FakeCohereOk.prompts.append(kwargs["messages"][1]["content"])
        return SimpleNamespace(message=SimpleNamespace(content=[SimpleNamespace(text="High-level methodology guidance.")]))


class _FakeCohereDown:
    def __init__(self, *args, **kwargs):
        pass

    def chat(self, *args, **kwargs):
        raise RuntimeError("simulated Cohere outage (429/5xx/network/timeout)")


def _project_with_task_and_evidence(name: str):
    saved = {k: v for k, v in os.environ.items() if k in ("CO_API_KEY", "COHERE_API_KEY")}
    for key in saved:
        del os.environ[key]
    try:
        project = client.post("/api/v1/projects", json={"name": name}).json()
        project_id = project["id"]
        client.put(
            f"/api/v1/projects/{project_id}/scope",
            json={"in_scope_whitelist": ["target.local"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
        )
        client.post(f"/api/v1/projects/{project_id}/scope/lock")
        task = client.get(f"/api/v1/projects/{project_id}/tasks").json()[0]["tasks"][0]
        verification = client.post(
            f"/api/v1/projects/{project_id}/tasks/{task['id']}/verify",
            json={"raw_content": "GET /backup.zip -> 200 OK"},
        )
        assert verification.status_code == 200
        return project_id, task
    finally:
        os.environ.update(saved)


def _mentor(project_id, task, body):
    return client.post(f"/api/v1/projects/{project_id}/tasks/{task['id']}/mentor", json=body)


def test_mentor_rejects_invalid_mode_and_unknown_task():
    project = client.post("/api/v1/projects", json={"name": "Mentor Schema"}).json()
    project_id = project["id"]
    task = client.get(f"/api/v1/projects/{project_id}/tasks").json()[0]["tasks"][0]
    invalid_mode = _mentor(project_id, task, {"mode": "attack", "user_message": "help"})
    assert invalid_mode.status_code == 422
    empty_message = _mentor(project_id, task, {"mode": "teach", "user_message": ""})
    assert empty_message.status_code == 422
    unknown_task = client.post(
        f"/api/v1/projects/{project_id}/tasks/not-a-task/mentor",
        json={"mode": "teach", "user_message": "help"},
    )
    assert unknown_task.status_code == 404


def test_mentor_offline_returns_static_checklist(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id, task = _project_with_task_and_evidence("Mentor Offline")
    response = _mentor(project_id, task, {"mode": "guide", "user_message": "Which tool fits this task?"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "guide"
    assert data["ai_available"] is False
    assert "unavailable" in data["reply"].lower()
    assert "checklist" in data["reply"].lower()


def test_mentor_live_call_includes_bounded_context_pack(monkeypatch):
    _FakeCohereOk.prompts = []
    monkeypatch.setenv("CO_API_KEY", "test-key")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", _FakeCohereOk)
    project_id, task = _project_with_task_and_evidence("Mentor Context Pack")
    response = _mentor(project_id, task, {
        "mode": "verify",
        "user_message": "What does my evidence show?",
        "target_host": "target.local",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ai_available"] is True
    assert data["reply"] == "High-level methodology guidance."
    prompt = _FakeCohereOk.prompts[-1]
    assert task["title"] in prompt
    assert "target.local" in prompt
    assert "whitelist" in prompt
    assert "200 OK" in prompt, "Evidence excerpt must be included as context"
    assert len(json.dumps(prompt)) < 20000, "Context pack must stay bounded"


def test_mentor_cohere_failure_returns_safe_fallback(monkeypatch):
    monkeypatch.setenv("CO_API_KEY", "test-key-down")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", _FakeCohereDown)
    project_id, task = _project_with_task_and_evidence("Mentor Outage")
    response = _mentor(project_id, task, {"mode": "teach", "user_message": "Explain this phase"})
    assert response.status_code == 200
    data = response.json()
    assert data["ai_available"] is False
    assert "unavailable" in data["reply"].lower()
    assert "checklist" in data["reply"].lower()
    events = client.get(f"/api/v1/projects/{project_id}/audit-log").json()
    assert any(event["event_type"] == "MENTOR_ASKED" for event in events)


def test_mentor_rejects_out_of_scope_target():
    project_id, task = _project_with_task_and_evidence("Mentor Scope Gate")
    response = _mentor(project_id, task, {"mode": "teach", "user_message": "Explain", "target_host": "evil.example.com"})
    assert response.status_code == 422
    assert "whitelist" in response.json()["detail"].lower()
