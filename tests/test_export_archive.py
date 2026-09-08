import io
import json
import zipfile

from fastapi.testclient import TestClient
from backend.main import app


def make_project_with_evidence(client):
    project = client.post('/api/v1/projects', json={'name': 'Export Archive Test'}).json()
    project_id = project['id']
    client.put(f'/api/v1/projects/{project_id}/scope', json={'in_scope_whitelist':['target.local'], 'out_of_scope_blacklist':[], 'max_rate_limit':10})
    client.post(f'/api/v1/projects/{project_id}/scope/lock')
    task = client.get(f'/api/v1/projects/{project_id}/tasks').json()[0]['tasks'][0]
    evidence = client.post(f'/api/v1/projects/{project_id}/tasks/{task["id"]}/verify', json={'raw_content':'plain archive evidence /backup.zip'}).json()
    return project_id, evidence['evidence_id']


def test_export_returns_project_zip_with_manifest_and_artifact(monkeypatch):
    monkeypatch.delenv('CO_API_KEY', raising=False)
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    client = TestClient(app)
    project_id, evidence_id = make_project_with_evidence(client)
    response = client.get(f'/api/v1/projects/{project_id}/export')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = archive.namelist()
        assert 'manifest.json' in names
        assert 'db/project_data.json' in names
        assert any(name.startswith('artifacts/') and evidence_id in name for name in names)
        manifest = json.loads(archive.read('manifest.json'))
        assert manifest['format_version'] == '1.0'
        assert manifest['project_id'] == project_id
        assert not any('.env' in name.lower() or 'api_key' in name.lower() for name in names)
