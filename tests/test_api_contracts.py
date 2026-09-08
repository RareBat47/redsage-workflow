from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

CANONICAL_ROUTE_CONTRACT = frozenset({
    ("GET", "/api/v1/health"),
    ("GET", "/api/v1/projects"),
    ("POST", "/api/v1/projects"),
    ("GET", "/api/v1/projects/{project_id}"),
    ("GET", "/api/v1/projects/{project_id}/scope"),
    ("PUT", "/api/v1/projects/{project_id}/scope"),
    ("POST", "/api/v1/projects/{project_id}/scope/lock"),
    ("POST", "/api/v1/projects/{project_id}/scope/amend"),
    ("GET", "/api/v1/projects/{project_id}/tasks"),
    ("POST", "/api/v1/projects/{project_id}/tasks/{task_id}/state"),
    ("POST", "/api/v1/projects/{project_id}/tasks/{task_id}/verify"),
    ("POST", "/api/v1/projects/{project_id}/tasks/{task_id}/mentor"),
    ("GET", "/api/v1/projects/{project_id}/evidence"),
    ("GET", "/api/v1/projects/{project_id}/evidence/{evidence_id}/content"),
    ("GET", "/api/v1/projects/{project_id}/proposals"),
    ("POST", "/api/v1/projects/{project_id}/proposals/{proposal_id}/approve"),
    ("POST", "/api/v1/projects/{project_id}/proposals/{proposal_id}/dismiss"),
    ("POST", "/api/v1/projects/{project_id}/proposals/{proposal_id}/undo"),
    ("GET", "/api/v1/projects/{project_id}/findings"),
    ("POST", "/api/v1/projects/{project_id}/findings"),
    ("POST", "/api/v1/projects/{project_id}/findings/{finding_id}/confirm"),
    ("GET", "/api/v1/projects/{project_id}/report"),
    ("GET", "/api/v1/projects/{project_id}/report/download"),
    ("GET", "/api/v1/projects/{project_id}/report/readiness"),
    ("GET", "/api/v1/projects/{project_id}/export"),
    ("POST", "/api/v1/projects/import"),
    ("GET", "/api/v1/projects/{project_id}/assets"),
    ("POST", "/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks"),
    ("GET", "/api/v1/projects/{project_id}/audit-log"),
    ("GET", "/api/v1/projects/{project_id}/search"),
})


def test_canonical_route_contract():
    actual = frozenset(
        (method.upper(), path)
        for path, path_item in app.openapi().get("paths", {}).items()
        for method in path_item
        if method.upper() in {"GET", "POST", "PUT", "DELETE", "PATCH"}
    )
    assert CANONICAL_ROUTE_CONTRACT <= actual, CANONICAL_ROUTE_CONTRACT - actual


def test_invalid_resource_identifier_has_safe_error_shape():
    response = client.get("/api/v1/projects/not-a-real-project")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "traceback" not in response.text.lower()
