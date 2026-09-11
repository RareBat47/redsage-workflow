from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_project_brief_is_readable_writable_and_clearable():
    project = client.post("/api/v1/projects", json={"name": "Brief API Test"}).json()
    project_id = project["id"]

    assert project["brief"] is None
    assert client.get(f"/api/v1/projects/{project_id}").json()["brief"] is None

    updated = client.put(
        f"/api/v1/projects/{project_id}/brief",
        json={"text": "  Authorized web review during the maintenance window.  "},
    )
    assert updated.status_code == 200
    assert updated.json()["brief"] == "Authorized web review during the maintenance window."
    assert client.get(f"/api/v1/projects/{project_id}").json()["brief"] == updated.json()["brief"]

    cleared = client.put(f"/api/v1/projects/{project_id}/brief", json={"text": "   "})
    assert cleared.status_code == 200
    assert cleared.json()["brief"] == ""


def test_project_brief_route_rejects_unknown_project():
    response = client.put("/api/v1/projects/not-a-real-project/brief", json={"text": "brief"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
