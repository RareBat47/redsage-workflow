from fastapi.testclient import TestClient
from backend.main import app
import uuid

def test_proposal_approval_can_be_undone_when_untouched():
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Undo Test'}).json(); project_id = project['id']
    client.put(f'/api/v1/projects/{project_id}/scope', json={'in_scope_whitelist':['target.local'], 'out_of_scope_blacklist':[], 'max_rate_limit':10}); client.post(f'/api/v1/projects/{project_id}/scope/lock')
    from backend.database import SessionLocal
    from backend.models.schema import WorkflowProposal
    proposal_id = f'proposal-{uuid.uuid4()}'
    db = SessionLocal(); proposal = WorkflowProposal(id=proposal_id, project_id=project_id, phase_name='Phase 4: Vulnerability Analysis', title='Review asset', objective='Review authorized evidence', priority='MEDIUM', target_asset='/review', action_type='ASSET_REVIEW'); db.add(proposal); db.commit(); db.close()
    approved = client.post(f'/api/v1/projects/{project_id}/proposals/{proposal_id}/approve'); assert approved.status_code == 200
    events = client.get(f'/api/v1/projects/{project_id}/audit-log').json(); assert any(event['can_undo'] for event in events if event['event_type'] == 'PROPOSAL_APPROVED')
    undone = client.post(f'/api/v1/projects/{project_id}/proposals/{proposal_id}/undo'); assert undone.status_code == 200
    assert any(event['event_type'] == 'PROPOSAL_UNDONE' for event in client.get(f'/api/v1/projects/{project_id}/audit-log').json())
