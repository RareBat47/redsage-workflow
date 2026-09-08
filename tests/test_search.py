from fastapi.testclient import TestClient
from backend.main import app
import uuid

def test_project_search_returns_grouped_matches():
    client = TestClient(app); project = client.post('/api/v1/projects', json={'name': 'Search Test'}).json(); project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset, Finding
    asset_id = f'asset-{uuid.uuid4()}'; finding_id = f'finding-{uuid.uuid4()}'
    db = SessionLocal(); db.add(Asset(id=asset_id, project_id=project_id, type='HOST', value='search-target.local')); db.add(Finding(id=finding_id, project_id=project_id, title='Search finding', severity='LOW', status='DRAFT', description='searchable description', reproduction_steps='steps')); db.commit(); db.close()
    result = client.get(f'/api/v1/projects/{project_id}/search?q=search'); assert result.status_code == 200
    assert result.json()['assets'][0]['id'] == asset_id; assert result.json()['findings'][0]['id'] == finding_id
