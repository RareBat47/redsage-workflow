"""Cohere failure resilience tests.

Simulates a configured Cohere key whose live request fails (429/5xx/network/
timeout) and asserts the verify endpoint degrades to a safe structured
AMBIGUOUS/LOW verdict instead of raising HTTP 500, while the evidence artifact
and its metadata are still persisted.
"""

import cohere as cohere_module
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.cohere_service import verify_task_evidence


class _ExplodingClientV2:
    def __init__(self, *args, **kwargs):
        pass

    def chat(self, *args, **kwargs):
        raise RuntimeError("simulated Cohere outage (429/5xx/network/timeout)")


def _force_cohere_outage(monkeypatch):
    monkeypatch.setenv("CO_API_KEY", "test-key-configured-but-provider-down")
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    monkeypatch.setattr(cohere_module, "ClientV2", _ExplodingClientV2)


def test_verifier_falls_back_to_ambiguous_low_on_cohere_failure(monkeypatch):
    _force_cohere_outage(monkeypatch)
    verdict = verify_task_evidence(
        "Port discovery",
        "Identify open ports",
        "scan started\nhttps://target.local/backup.zip [200]\nhost down for remaining ports",
    )
    assert verdict.verdict == "AMBIGUOUS"
    assert verdict.confidence == "LOW"
    assert verdict.summary == "AI verification unavailable; evidence saved; manual review recommended."
    assert verdict.grounded_quotations, "Fallback must quote the submitted evidence"
    assert all(quote in "scan started\nhttps://target.local/backup.zip [200]\nhost down for remaining ports" or quote == "Evidence submitted for analyst review" for quote in verdict.grounded_quotations)
    assert any(asset.value == "https://target.local/backup.zip" for asset in verdict.extracted_assets)


def test_verifier_offline_is_ambiguous_and_never_passes(monkeypatch):
    monkeypatch.delenv("CO_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    verdict = verify_task_evidence("Review checkpoint", "Confirm the checkpoint", "checkpoint complete")
    assert verdict.verdict == "AMBIGUOUS"
    assert verdict.confidence == "LOW"
    assert "manual review" in verdict.summary


def test_verify_endpoint_never_500s_and_still_stores_evidence(monkeypatch, tmp_path):
    from backend.services import artifact_manager

    monkeypatch.setattr(artifact_manager, "ARTIFACTS_ROOT", tmp_path / "projects")
    _force_cohere_outage(monkeypatch)
    client = TestClient(app)
    project = client.post("/api/v1/projects", json={"name": "Cohere Outage Test"}).json()
    project_id = project["id"]
    client.put(
        f"/api/v1/projects/{project_id}/scope",
        json={"in_scope_whitelist": ["target.local"], "out_of_scope_blacklist": [], "max_rate_limit": 10},
    )
    client.post(f"/api/v1/projects/{project_id}/scope/lock")
    task = client.get(f"/api/v1/projects/{project_id}/tasks").json()[0]["tasks"][0]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks/{task['id']}/verify",
        json={"raw_content": "connection reset by peer during scan\n/backup.zip found"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "AMBIGUOUS"
    assert data["confidence"] == "LOW"
    assert "AI verification unavailable" in data["summary"]
    assert data["task_status"] == "NOT_STARTED", "Ambiguous verdicts must not auto-complete the task"

    evidence_id = data["evidence_id"]
    records = client.get(f"/api/v1/projects/{project_id}/evidence").json()
    record = next(item for item in records if item["evidence_id"] == evidence_id)
    assert record["file_path"].endswith(".txt")
    assert record["file_size_bytes"] > 0
    assert len(record["sha256_hash"]) == 64
    content = client.get(f"/api/v1/projects/{project_id}/evidence/{evidence_id}/content")
    assert content.status_code == 200
    assert "/backup.zip found" in content.json()["content"]
