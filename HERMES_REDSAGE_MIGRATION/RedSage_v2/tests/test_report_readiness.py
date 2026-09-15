from fastapi.testclient import TestClient
from backend.main import app
import uuid

def test_readiness_flags_missing_evidence_and_coverage():
    client = TestClient(app); project = client.post('/api/v1/projects', json={'name': 'Readiness Test'}).json(); project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Finding
    db = SessionLocal(); db.add(Finding(id=f'readiness-{uuid.uuid4()}', project_id=project_id, title='Incomplete finding', severity='HIGH', status='CONFIRMED', description='Description', reproduction_steps='', remediation=None, evidence_id=None)); db.commit(); db.close()
    result = client.get(f'/api/v1/projects/{project_id}/report/readiness'); assert result.status_code == 200
    assert result.json()['ready_for_export'] is False
    assert any(issue['severity'] == 'CRITICAL' for issue in result.json()['issues'])
