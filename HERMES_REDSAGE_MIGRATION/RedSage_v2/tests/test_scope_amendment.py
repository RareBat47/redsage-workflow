from fastapi.testclient import TestClient
from backend.main import app

def test_scope_amendment_updates_scope_and_audit():
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Amendment Test'}).json()
    project_id = project['id']
    client.put(f'/api/v1/projects/{project_id}/scope', json={'in_scope_whitelist':['target.local'], 'out_of_scope_blacklist':[], 'max_rate_limit':10})
    client.post(f'/api/v1/projects/{project_id}/scope/lock')
    amended = client.post(f'/api/v1/projects/{project_id}/scope/amend', json={'additional_targets':['api.target.local'], 'authorized_by':'Client SecOps', 'rationale':'Client approved the newly discovered host.'})
    assert amended.status_code == 200
    assert 'api.target.local' in client.get(f'/api/v1/projects/{project_id}/scope').json()['in_scope_whitelist']
    assert any(event['event_type'] == 'SCOPE_AMENDED' for event in client.get(f'/api/v1/projects/{project_id}/audit-log').json())
