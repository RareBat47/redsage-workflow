"""Baseline methodology seeding tests: new projects must receive 7 PTES phases."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

EXPECTED_PHASES = [
    "Phase 1: Pre-engagement",
    "Phase 2: Intelligence Gathering",
    "Phase 3: Threat Modeling",
    "Phase 4: Vulnerability Analysis",
    "Phase 5: Exploitation (Authorized Validation)",
    "Phase 6: Post-Exploitation (Impact Review)",
    "Phase 7: Reporting",
]


def test_new_project_seeds_seven_phases_in_order():
    project = client.post("/api/v1/projects", json={"name": "Seven Phase Seed Test"}).json()
    phases = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    assert [phase["name"] for phase in phases] == EXPECTED_PHASES
    assert [phase["order_index"] for phase in phases] == list(range(1, 8))


def test_phase_task_counts_stay_minimal_and_safe():
    project = client.post("/api/v1/projects", json={"name": "Seed Task Counts Test"}).json()
    phases = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    total = 0
    for phase in phases:
        assert 1 <= len(phase["tasks"]) <= 3, f"{phase['name']} should have 1-3 tasks"
        total += len(phase["tasks"])
    assert 12 <= total <= 16


def test_command_templates_only_cover_safe_recon_tasks():
    project = client.post("/api/v1/projects", json={"name": "Seed Command Safety Test"}).json()
    phases = client.get(f"/api/v1/projects/{project['id']}/tasks").json()
    templates = [task["command_template"] for phase in phases for task in phase["tasks"] if task["command_template"]]
    assert templates, "Seeded methodology should retain its auditing commands"
    for template in templates:
        lowered = template.lower()
        assert "{target_host}" in lowered
        assert not any(bad in lowered for bad in ("exploit", "payload", "reverse", "shell -c", "nc -e", "hydra", "sqlmap"))
    # Exploitation and post-exploitation phases stay planning/documentation only.
    phase5 = next(phase for phase in phases if phase["name"].startswith("Phase 5"))
    phase6 = next(phase for phase in phases if phase["name"].startswith("Phase 6"))
    assert all(task["command_template"] is None for task in phase5["tasks"])
    assert all(task["command_template"] is None for task in phase6["tasks"])


def test_proposal_approval_still_targets_vulnerability_analysis_phase():
    import uuid

    from backend.database import SessionLocal
    from backend.models.schema import WorkflowProposal

    project = client.post("/api/v1/projects", json={"name": "Proposal Phase Link Test"}).json()
    project_id = project["id"]
    proposal_id = f"proposal-{uuid.uuid4()}"
    db = SessionLocal()
    db.add(WorkflowProposal(id=proposal_id, project_id=project_id, phase_name="Phase 4: Vulnerability Analysis", title="Review seeded asset", objective="Review authorized evidence", priority="MEDIUM", target_asset="/review", action_type="ASSET_REVIEW"))
    db.commit()
    db.close()
    approved = client.post(f"/api/v1/projects/{project_id}/proposals/{proposal_id}/approve")
    assert approved.status_code == 200
    phases = {phase["name"]: phase for phase in client.get(f"/api/v1/projects/{project_id}/tasks").json()}
    assert any(task["title"] == "Review seeded asset" for task in phases["Phase 4: Vulnerability Analysis"]["tasks"])


def test_proposal_approval_honors_non_phase_four_target():
    import uuid

    from backend.database import SessionLocal
    from backend.models.schema import WorkflowProposal

    project = client.post("/api/v1/projects", json={"name": "Cross Phase Proposal Test"}).json()
    project_id = project["id"]
    proposal_id = f"proposal-{uuid.uuid4()}"
    db = SessionLocal()
    db.add(WorkflowProposal(
        id=proposal_id,
        project_id=project_id,
        phase_name="Phase 2: Intelligence Gathering",
        title="Review intelligence asset",
        objective="Review authorized intelligence evidence",
        priority="MEDIUM",
        target_asset="/discovered-resource",
        action_type="INVESTIGATION",
    ))
    db.commit()
    db.close()

    approved = client.post(f"/api/v1/projects/{project_id}/proposals/{proposal_id}/approve")
    assert approved.status_code == 200

    phases = {phase["name"]: phase for phase in client.get(f"/api/v1/projects/{project_id}/tasks").json()}
    assert any(task["title"] == "Review intelligence asset" for task in phases["Phase 2: Intelligence Gathering"]["tasks"])
    assert not any(task["title"] == "Review intelligence asset" for task in phases["Phase 4: Vulnerability Analysis"]["tasks"])


def test_proposal_approval_rejects_unknown_target_phase_without_creating_task():
    import uuid

    from backend.database import SessionLocal
    from backend.models.schema import Task, WorkflowProposal

    project = client.post("/api/v1/projects", json={"name": "Missing Proposal Phase Test"}).json()
    project_id = project["id"]
    proposal_id = f"proposal-{uuid.uuid4()}"
    db = SessionLocal()
    db.add(WorkflowProposal(
        id=proposal_id,
        project_id=project_id,
        phase_name="Phase 99: Missing",
        title="Should not be created",
        objective="Review authorized evidence",
        priority="LOW",
        target_asset="/missing-phase-resource",
        action_type="INVESTIGATION",
    ))
    db.commit()
    task_count = db.query(Task).filter(Task.project_id == project_id).count()
    db.close()

    response = client.post(f"/api/v1/projects/{project_id}/proposals/{proposal_id}/approve")
    assert response.status_code == 400
    assert "target phase" in response.json()["detail"]

    db = SessionLocal()
    assert db.query(Task).filter(Task.project_id == project_id).count() == task_count
    db.close()


def test_proposal_approval_error_names_the_missing_phase():
    import uuid

    from backend.database import SessionLocal
    from backend.models.schema import WorkflowProposal

    project = client.post("/api/v1/projects", json={"name": "Missing Phase Detail Test"}).json()
    project_id = project["id"]
    proposal_id = f"proposal-{uuid.uuid4()}"
    db = SessionLocal()
    db.add(WorkflowProposal(
        id=proposal_id,
        project_id=project_id,
        phase_name="Phase 9: Does Not Exist",
        title="Should not be created",
        objective="Review authorized evidence",
        priority="LOW",
        target_asset="/missing-phase-resource",
        action_type="INVESTIGATION",
    ))
    db.commit()
    db.close()

    response = client.post(f"/api/v1/projects/{project_id}/proposals/{proposal_id}/approve")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "target phase" in detail
    assert "Phase 9: Does Not Exist" in detail
