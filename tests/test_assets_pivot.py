from fastapi.testclient import TestClient
from backend.main import app
import uuid

def test_asset_suggestions_are_pending_and_deduplicated(monkeypatch):
    monkeypatch.delenv('CO_API_KEY', raising=False)
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Asset Pivot Test'}).json(); project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset
    asset_id = f'asset-{uuid.uuid4()}'
    db = SessionLocal(); asset = Asset(id=asset_id, project_id=project_id, type='HOST', value='target.local'); db.add(asset); db.commit(); db.close()
    first = client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks'); assert first.status_code == 200; assert first.json()['created_count'] == 1
    second = client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks'); assert second.json()['created_count'] == 0
    assert len(client.get(f'/api/v1/projects/{project_id}/proposals').json()) == 1
