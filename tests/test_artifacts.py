import hashlib

import pytest
from fastapi.testclient import TestClient

from backend.services import artifact_manager
from backend.main import app


def test_artifact_path_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        artifact_manager.safe_join(tmp_path, "../../etc/passwd")


def test_saved_artifact_digest_matches_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(artifact_manager, "ARTIFACTS_ROOT", tmp_path / "projects")
    relative, size, digest, filename = artifact_manager.save_artifact("project-1", "EVID-TEST", "sample output")
    content = (tmp_path / "projects" / "project-1" / "artifacts" / filename).read_bytes()
    assert relative.endswith(filename)
    assert size == len(content)
    assert digest == hashlib.sha256(content).hexdigest()


def test_evidence_list_returns_metadata_and_excerpt(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    client = TestClient(app)
    project = client.post("/api/v1/projects", json={"name": "Artifact Metadata Test"}).json()
    project_id = project["id"]
    client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["target.local"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    client.post(f"/api/v1/projects/{project_id}/scope/lock")
    task = client.get(f"/api/v1/projects/{project_id}/tasks").json()[0]["tasks"][0]
    verification = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/verify",
        json={"raw_content": 'password="not-stored-in-excerpt"\nplain evidence'},
    )
    assert verification.status_code == 200
    evidence_id = verification.json()["evidence_id"]
    records = client.get(f"/api/v1/projects/{project_id}/evidence")
    assert records.status_code == 200
    item = next(record for record in records.json() if record["evidence_id"] == evidence_id)
    assert item["file_path"].endswith(".txt")
    assert item["file_size_bytes"] > 0
    assert len(item["sha256_hash"]) == 64
    assert "not-stored-in-excerpt" not in item["redacted_excerpt"]
