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


def test_refiner_can_target_a_non_phase_four_phase_and_approval_honors_it(monkeypatch):
    import cohere as cohere_module

    class Content:
        text = '{"proposals":[{"title":"Review intelligence evidence","objective":"Review the discovered asset in the intelligence phase.","command_template":null,"priority":"HIGH","phase_name":"Phase 2: Intelligence Gathering"}]}'

    class Message:
        content = [Content()]

    class Response:
        message = Message()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            return Response()

    monkeypatch.setenv('CO_API_KEY', 'refiner-test-key')
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    monkeypatch.setattr(cohere_module, 'ClientV2', FakeClient)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Cross Phase Refiner Test'}).json()
    project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset

    asset_id = f'asset-{uuid.uuid4()}'
    db = SessionLocal()
    db.add(Asset(id=asset_id, project_id=project_id, type='ENDPOINT', value='https://target.local/catalog'))
    db.commit()
    db.close()

    created = client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks')
    assert created.status_code == 200
    proposal = client.get(f'/api/v1/projects/{project_id}/proposals').json()[0]
    assert proposal['phase_name'] == 'Phase 2: Intelligence Gathering'

    approved = client.post(f"/api/v1/projects/{project_id}/proposals/{proposal['id']}/approve")
    assert approved.status_code == 200
    phases = {phase['name']: phase for phase in client.get(f'/api/v1/projects/{project_id}/tasks').json()}
    assert any(task['title'] == proposal['title'] for task in phases['Phase 2: Intelligence Gathering']['tasks'])
    assert not any(task['title'] == proposal['title'] for task in phases['Phase 4: Vulnerability Analysis']['tasks'])


def test_refiner_invalid_phase_falls_back_to_phase_four(monkeypatch):
    import cohere as cohere_module

    class Content:
        text = '{"proposals":[{"title":"Review invalid phase asset","objective":"Review the discovered asset safely.","command_template":null,"priority":"MEDIUM","phase_name":"Phase 99: Invalid"}]}'

    class Message:
        content = [Content()]

    class Response:
        message = Message()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            return Response()

    monkeypatch.setenv('CO_API_KEY', 'refiner-invalid-key')
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    monkeypatch.setattr(cohere_module, 'ClientV2', FakeClient)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Invalid Refiner Phase Test'}).json()
    project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset

    asset_id = f'asset-{uuid.uuid4()}'
    db = SessionLocal()
    db.add(Asset(id=asset_id, project_id=project_id, type='FILE', value='/backup.zip'))
    db.commit()
    db.close()
    assert client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks').status_code == 200
    proposal = client.get(f'/api/v1/projects/{project_id}/proposals').json()[0]
    assert proposal['phase_name'] == 'Phase 4: Vulnerability Analysis'


def _empty_proposals_client(monkeypatch):
    import cohere as cohere_module

    class Content:
        text = '{"proposals": []}'

    class Message:
        content = [Content()]

    class Response:
        message = Message()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            return Response()

    monkeypatch.setenv('CO_API_KEY', 'refiner-empty-key')
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    monkeypatch.setattr(cohere_module, 'ClientV2', FakeClient)


def test_refiner_empty_response_falls_back_to_standard_proposal(monkeypatch):
    _empty_proposals_client(monkeypatch)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Empty Refiner Response Test'}).json()
    project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset

    asset_id = f'asset-{uuid.uuid4()}'
    db = SessionLocal()
    db.add(Asset(id=asset_id, project_id=project_id, type='FILE', value='/backup.zip'))
    db.commit()
    db.close()

    response = client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks')
    assert response.status_code == 200
    assert response.json()['created_count'] == 1
    assert client.get(f'/api/v1/projects/{project_id}/proposals').json()[0]['phase_name'] == 'Phase 4: Vulnerability Analysis'


def test_keyword_discovery_never_500s_when_refiner_returns_empty(monkeypatch):
    _empty_proposals_client(monkeypatch)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Empty Refiner Verify Test'}).json()
    project_id = project['id']
    client.put(
        f'/api/v1/projects/{project_id}/scope',
        json={'in_scope_whitelist': ['target.local'], 'out_of_scope_blacklist': [], 'max_rate_limit': 10},
    )
    client.post(f'/api/v1/projects/{project_id}/scope/lock')
    task = client.get(f'/api/v1/projects/{project_id}/tasks').json()[0]['tasks'][0]

    response = client.post(
        f'/api/v1/projects/{project_id}/tasks/{task["id"]}/verify',
        json={'raw_content': 'review complete https://target.local/backup.zip'},
    )
    assert response.status_code == 200
    proposals = client.get(f'/api/v1/projects/{project_id}/proposals').json()
    assert len(proposals) == 1
    assert proposals[0]['phase_name'] == 'Phase 4: Vulnerability Analysis'


def test_offline_suggestion_defaults_to_phase_four(monkeypatch):
    """No API key: phase choice must stay Phase 4 exactly as before this feature."""
    monkeypatch.delenv('CO_API_KEY', raising=False)
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Offline Phase Default Test'}).json()
    project_id = project['id']
    from backend.database import SessionLocal
    from backend.models.schema import Asset

    asset_id = f'asset-{uuid.uuid4()}'
    db = SessionLocal()
    db.add(Asset(id=asset_id, project_id=project_id, type='FILE', value='/backup.zip'))
    db.commit()
    db.close()

    assert client.post(f'/api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks').status_code == 200
    proposal = client.get(f'/api/v1/projects/{project_id}/proposals').json()[0]
    assert proposal['phase_name'] == 'Phase 4: Vulnerability Analysis'


def test_keyword_discovery_uses_ai_selected_phase(monkeypatch):
    """Keyword trigger path: AI picks Phase 5; stored phase_name and approval must honor it."""
    import cohere as cohere_module

    class Content:
        text = '{"proposals":[{"title":"Review validation evidence","objective":"Review the discovered asset during authorized validation.","command_template":null,"priority":"HIGH","phase_name":"Phase 5: Exploitation (Authorized Validation)"}]}'

    class Message:
        content = [Content()]

    class Response:
        message = Message()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def chat(self, *args, **kwargs):
            return Response()

    monkeypatch.setenv('CO_API_KEY', 'refiner-keyword-phase-key')
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    monkeypatch.setattr(cohere_module, 'ClientV2', FakeClient)
    client = TestClient(app)
    project = client.post('/api/v1/projects', json={'name': 'Keyword Phase Selection Test'}).json()
    project_id = project['id']
    client.put(
        f'/api/v1/projects/{project_id}/scope',
        json={'in_scope_whitelist': ['target.local'], 'out_of_scope_blacklist': [], 'max_rate_limit': 10},
    )
    client.post(f'/api/v1/projects/{project_id}/scope/lock')
    task = client.get(f'/api/v1/projects/{project_id}/tasks').json()[0]['tasks'][0]

    verified = client.post(
        f'/api/v1/projects/{project_id}/tasks/{task["id"]}/verify',
        json={'raw_content': 'review complete https://target.local/backup.zip'},
    )
    assert verified.status_code == 200

    proposals = client.get(f'/api/v1/projects/{project_id}/proposals').json()
    assert len(proposals) == 1
    assert proposals[0]['phase_name'] == 'Phase 5: Exploitation (Authorized Validation)'
    created_title = proposals[0]['title']

    approved = client.post(f"/api/v1/projects/{project_id}/proposals/{proposals[0]['id']}/approve")
    assert approved.status_code == 200
    phases = {phase['name']: phase for phase in client.get(f'/api/v1/projects/{project_id}/tasks').json()}
    assert any(item['title'] == created_title for item in phases['Phase 5: Exploitation (Authorized Validation)']['tasks'])
    assert not any(item['title'] == created_title for item in phases['Phase 4: Vulnerability Analysis']['tasks'])
