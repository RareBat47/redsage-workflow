"""Findings lifecycle tests: DRAFT creation, confirm gating, report filtering."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _locked_project_with_evidence(name: str, raw_content: str = "GET /login -> 200 OK"):
    import os

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
            json={"raw_content": raw_content},
        )
        assert verification.status_code == 200
        return project_id, verification.json()["evidence_id"]
    finally:
        os.environ.update(saved)


def test_draft_created_without_evidence_and_not_confirmed():
    project = client.post("/api/v1/projects", json={"name": "Draft No Evidence"}).json()
    project_id = project["id"]
    created = client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Suspicious exposure", "severity": "HIGH"},
    )
    assert created.status_code == 200
    assert created.json()["status"] == "drafted"
    listing = client.get(f"/api/v1/projects/{project_id}/findings").json()
    assert len(listing) == 1
    assert listing[0]["status"] == "DRAFT"
    assert listing[0]["evidence_id"] is None


def test_draft_rejects_unknown_evidence_reference():
    project = client.post("/api/v1/projects", json={"name": "Draft Bad Evidence"}).json()
    project_id = project["id"]
    created = client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Draft", "evidence_id": "EVID-DOES-NOT-EXIST"},
    )
    assert created.status_code == 400


def test_confirm_requires_valid_evidence_and_fields():
    project_id, evidence_id = _locked_project_with_evidence("Confirm Gating")
    draft = client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Backup archive exposed", "severity": "HIGH"},
    ).json()

    confirm_no_evidence = client.post(
        f"/api/v1/projects/{project_id}/findings/{draft['finding_id']}/confirm",
        json={"evidence_id": "EVID-DOES-NOT-EXIST"},
    )
    assert confirm_no_evidence.status_code == 422
    assert "evidence" in confirm_no_evidence.json()["detail"].lower()

    confirm_missing_fields = client.post(
        f"/api/v1/projects/{project_id}/findings/{draft['finding_id']}/confirm",
        json={"evidence_id": evidence_id},
    )
    assert confirm_missing_fields.status_code == 422
    detail = confirm_missing_fields.json()["detail"]
    assert "description" in detail and "reproduction_steps" in detail

    confirm_ok = client.post(
        f"/api/v1/projects/{project_id}/findings/{draft['finding_id']}/confirm",
        json={
            "evidence_id": evidence_id,
            "description": "Publicly accessible backup archive on the target.",
            "reproduction_steps": "Navigate to the URL identified in the linked evidence and observe the response.",
        },
    )
    assert confirm_ok.status_code == 200
    assert confirm_ok.json()["status"] == "confirmed"

    double_confirm = client.post(
        f"/api/v1/projects/{project_id}/findings/{draft['finding_id']}/confirm",
        json={"evidence_id": evidence_id, "description": "x", "reproduction_steps": "y"},
    )
    assert double_confirm.status_code == 400

    listing = client.get(f"/api/v1/projects/{project_id}/findings").json()
    finding = next(item for item in listing if item["id"] == draft["finding_id"])
    assert finding["status"] == "CONFIRMED"
    assert finding["evidence_id"] == evidence_id


def test_report_includes_only_confirmed_findings_and_drafts_do_not_block():
    project_id, evidence_id = _locked_project_with_evidence("Report Filter")
    confirmed = client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Confirmed exposure", "severity": "HIGH", "description": "d", "reproduction_steps": "r", "evidence_id": evidence_id},
    ).json()
    client.post(
        f"/api/v1/projects/{project_id}/findings/{confirmed['finding_id']}/confirm",
        json={"evidence_id": evidence_id},
    )
    client.post(
        f"/api/v1/projects/{project_id}/findings",
        json={"title": "Draft only exposure", "severity": "LOW", "description": "draft body", "reproduction_steps": ""},
    )
    report = client.get(f"/api/v1/projects/{project_id}/report").json()["markdown"]
    assert "Confirmed exposure" in report
    assert "Draft only exposure" not in report

    readiness = client.get(f"/api/v1/projects/{project_id}/report/readiness").json()
    assert readiness["ready_for_export"] is True
    assert not any("Draft only exposure" in issue["message"] for issue in readiness["issues"])


def test_confirmed_missing_evidence_still_critical():
    import uuid

    project = client.post("/api/v1/projects", json={"name": "Legacy Confirmed"}).json()
    project_id = project["id"]
    from backend.database import SessionLocal
    from backend.models.schema import Finding

    db = SessionLocal()
    db.add(Finding(id=f"legacy-{uuid.uuid4()}", project_id=project_id, title="Legacy confirmed", severity="HIGH", status="CONFIRMED", description="d", reproduction_steps="r", evidence_id=None))
    db.commit()
    db.close()
    readiness = client.get(f"/api/v1/projects/{project_id}/report/readiness").json()
    assert readiness["ready_for_export"] is False
    assert any(issue["severity"] == "CRITICAL" for issue in readiness["issues"])
