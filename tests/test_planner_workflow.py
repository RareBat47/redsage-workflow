import copy
import json

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.planner_service import baseline_workflow_draft, canonical_phase_names, generate_workflow


client = TestClient(app)


COMPLETE_BRIEF = (
    "Authorized web application assessment of target.local for a two-day window. "
    "Scope is target.local and the staging application; constraints are safe, rate-limited, "
    "manual review only. Focus on evidence quality and the final report."
)


def make_project(brief: str | None = None):
    project = client.post("/api/v1/projects", json={"name": "Planner Test"}).json()
    if brief is not None:
        response = client.put(f"/api/v1/projects/{project['id']}/brief", json={"text": brief})
        assert response.status_code == 200
    return project


def test_incomplete_brief_returns_questions_and_no_draft(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project = make_project("Please create a workflow.")
    response = client.post(f"/api/v1/projects/{project['id']}/workflow/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NEEDS_CLARIFICATION"
    assert data["draft"] is None
    assert {item["id"] for item in data["questions"]} == {"engagement", "scope", "constraints", "timebox", "outcome"}


def test_offline_generation_uses_exact_baseline_shape_after_gate(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project = make_project(COMPLETE_BRIEF)
    response = client.post(f"/api/v1/projects/{project['id']}/workflow/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["ai_available"] is False
    assert [phase["name"] for phase in data["draft"]["phases"]] == canonical_phase_names()
    assert all(len(task["steps"]) == 1 for phase in data["draft"]["phases"] for task in phase["tasks"])
    assert all(not task["is_ai_proposed"] for phase in data["draft"]["phases"] for task in phase["tasks"])


def test_planner_provider_failure_falls_back_without_http_error(monkeypatch):
    import cohere as cohere_module

    class Down:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            raise RuntimeError("provider unavailable")

    monkeypatch.setenv("CO_API_KEY", "configured-but-down")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", Down)
    result = generate_workflow(COMPLETE_BRIEF)
    assert result["status"] == "READY"
    assert result["ai_available"] is False
    assert len(result["draft"]["phases"]) == 7


def test_three_complete_briefs_produce_different_mocked_live_drafts(monkeypatch):
    import cohere as cohere_module

    class Content:
        def __init__(self, text):
            self.text = text

    class Message:
        def __init__(self, text):
            self.content = [Content(text)]

    class Response:
        def __init__(self, text):
            self.message = Message(text)

    class FakeClient:
        briefs = []

        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            prompt = args[0] if args else kwargs["messages"][1]["content"]
            FakeClient.briefs.append(str(prompt))
            phases = []
            for index, name in enumerate(canonical_phase_names(), start=1):
                phases.append({"name": name, "order_index": index, "tasks": [{"title": f"Tailored {len(FakeClient.briefs)} {index}", "objective": "Review the authorized objective.", "steps": [{"title": "Capture checkpoint", "objective": "Record observations.", "why_it_matters": "Supports review.", "completion_criteria": "Evidence is captured.", "expected_evidence_type": "TERMINAL_LOG"}]}]})
            return Response(json.dumps({"phases": phases}))

    monkeypatch.setenv("CO_API_KEY", "planner-test-key")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", FakeClient)
    briefs = [
        COMPLETE_BRIEF,
        COMPLETE_BRIEF.replace("web application", "mobile application"),
        COMPLETE_BRIEF.replace("two-day", "one-week"),
    ]
    drafts = [generate_workflow(brief)["draft"] for brief in briefs]
    assert len({draft["phases"][0]["tasks"][0]["title"] for draft in drafts}) == 3
    assert all([phase["name"] for phase in draft["phases"]] == canonical_phase_names() for draft in drafts)


def test_generate_does_not_change_live_tasks_and_apply_replace_archives_old_rows(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project = make_project(COMPLETE_BRIEF)
    before = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    old_task_id = before[0]["tasks"][0]["id"]
    draft = client.post(f"/api/v1/projects/{project['id']}/workflow/generate").json()["draft"]
    after_generate = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    assert after_generate == before

    response = client.post(f"/api/v1/projects/{project['id']}/workflow/apply", json={"mode": "replace", "draft": draft})
    assert response.status_code == 200
    active = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    active_ids = {task["id"] for phase in active for task in phase["tasks"]}
    assert old_task_id not in active_ids

    from backend.database import SessionLocal
    from backend.models.schema import Task

    db = SessionLocal()
    old_task = db.query(Task).filter(Task.id == old_task_id).first()
    assert old_task is not None
    assert old_task.is_archived is True
    db.close()


def test_apply_merge_deduplicates_exact_active_titles(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project = make_project(COMPLETE_BRIEF)
    draft = baseline_workflow_draft().model_dump()
    first = client.post(f"/api/v1/projects/{project['id']}/workflow/apply", json={"mode": "merge", "draft": draft})
    assert first.status_code == 200
    before = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    second = client.post(f"/api/v1/projects/{project['id']}/workflow/apply", json={"mode": "merge", "draft": draft})
    assert second.status_code == 200
    after = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    assert sum(len(phase["tasks"]) for phase in after) == sum(len(phase["tasks"]) for phase in before)
