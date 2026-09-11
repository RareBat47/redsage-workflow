from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def make_task():
    project = client.post("/api/v1/projects", json={"name": "Task Steps Test"}).json()
    task = client.get(f"/api/v1/projects/{project['id']}/tasks").json()[0]["tasks"][0]
    return project["id"], task


def create_step(project_id: str, task_id: str, title: str):
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task_id}/steps",
        json={
            "title": title,
            "objective": f"Objective for {title}",
            "why_it_matters": "Keep the review bounded and documented.",
            "completion_criteria": "Capture sufficient human-reviewed evidence.",
            "expected_evidence_type": "TERMINAL_LOG",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_steps_can_be_created_listed_and_updated():
    project_id, task = make_task()
    step = create_step(project_id, task["id"], "First review checkpoint")
    assert step["status"] == "NOT_STARTED"
    assert step["order_index"] == 1

    listed = client.get(f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == step["id"]

    updated = client.put(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{step['id']}",
        json={
            "title": "Updated checkpoint",
            "objective": "Updated objective",
            "why_it_matters": "Updated rationale",
            "completion_criteria": "Updated criteria",
            "expected_evidence_type": "DOCUMENTATION",
            "order_index": 2,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated checkpoint"
    assert updated.json()["order_index"] == 2


def test_step_state_validation_and_rollup_require_all_active_steps_terminal():
    project_id, task = make_task()
    first = create_step(project_id, task["id"], "First checkpoint")
    second = create_step(project_id, task["id"], "Second checkpoint")

    missing_justification = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{first['id']}/state",
        json={"status": "SKIPPED", "justification": "no"},
    )
    assert missing_justification.status_code == 400

    first_done = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{first['id']}/state",
        json={"status": "COMPLETED"},
    )
    assert first_done.status_code == 200
    assert first_done.json()["task_status"] == "NOT_STARTED"

    second_done = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{second['id']}/state",
        json={"status": "CONFIRMED_NEGATIVE", "justification": "Reviewed and not present"},
    )
    assert second_done.status_code == 200
    assert second_done.json()["task_status"] == "COMPLETED"

    tasks = client.get(f"/api/v1/projects/{project_id}/tasks").json()
    selected = next(item for phase in tasks for item in phase["tasks"] if item["id"] == task["id"])
    assert selected["status"] == "COMPLETED"


def test_task_completion_is_guarded_when_active_steps_are_incomplete():
    project_id, task = make_task()
    create_step(project_id, task["id"], "Incomplete checkpoint")
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/state",
        json={"status": "COMPLETED"},
    )
    assert response.status_code == 409


def test_task_without_steps_keeps_direct_state_transition_behavior():
    project_id, task = make_task()
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/state",
        json={"status": "SKIPPED", "justification": "Not applicable for this review"},
    )
    assert response.status_code == 200
    assert response.json()["task_status"] == "SKIPPED"


def test_steps_are_scoped_to_the_parent_task_and_project():
    project_id, task = make_task()
    other_project_id, other_task = make_task()
    step = create_step(project_id, task["id"], "Scoped checkpoint")

    wrong_task = client.get(f"/api/v1/projects/{project_id}/tasks/{other_task['id']}/steps")
    assert wrong_task.status_code == 404
    wrong_project = client.put(
        f"/api/v1/projects/{other_project_id}/tasks/{other_task['id']}/steps/{step['id']}",
        json={"title": "Wrong scope", "objective": "", "why_it_matters": "", "completion_criteria": "", "expected_evidence_type": "TERMINAL_LOG"},
    )
    assert wrong_project.status_code == 404


def lock_project(project_id: str):
    response = client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["target.local"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    assert response.status_code == 200
    assert client.post(f"/api/v1/projects/{project_id}/scope/lock").status_code == 200


def test_step_verify_offline_is_ambiguous_and_persists_step_link(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id, task = make_task()
    step = create_step(project_id, task["id"], "Review evidence checkpoint")
    lock_project(project_id)

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{step['id']}/verify",
        json={"raw_content": "review complete\nhttps://target.local/archive.zip [200]"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "AMBIGUOUS"
    assert data["step_status"] == "NOT_STARTED"
    assert data["task_status"] == "NOT_STARTED"
    assert any(asset["value"] == "https://target.local/archive.zip" for asset in data["extracted_assets"])

    records = client.get(f"/api/v1/projects/{project_id}/evidence").json()
    record = next(item for item in records if item["evidence_id"] == data["evidence_id"])
    assert record["step_id"] == step["id"]
    assert record["step_title"] == step["title"]


def test_task_verify_is_rejected_when_active_steps_exist(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    project_id, task = make_task()
    create_step(project_id, task["id"], "Step-owned evidence")
    lock_project(project_id)

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/verify",
        json={"raw_content": "should not be persisted"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "this task uses step-level verification"
    assert client.get(f"/api/v1/projects/{project_id}/evidence").json() == []


def test_step_verify_uses_live_verdict_and_rolls_up(monkeypatch):
    import cohere as cohere_module

    class Content:
        text = '{"verdict":"PASS","confidence":"HIGH","summary":"Evidence meets the checkpoint.","grounded_quotations":["checkpoint complete"],"extracted_assets":[]}'

    class Message:
        content = [Content()]

    class Response:
        message = Message()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            return Response()

    monkeypatch.setenv("CO_API_KEY", "test-key")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", FakeClient)
    project_id, task = make_task()
    step = create_step(project_id, task["id"], "Live evidence checkpoint")
    lock_project(project_id)

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/steps/{step['id']}/verify",
        json={"raw_content": "checkpoint complete"},
    )
    assert response.status_code == 200
    assert response.json()["verdict"] == "PASS"
    assert response.json()["step_status"] == "COMPLETED"
    assert response.json()["task_status"] == "COMPLETED"
