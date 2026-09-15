import io
import json
import zipfile

from fastapi.testclient import TestClient
from backend.main import app


def test_import_exported_archive_creates_remapped_project_with_artifact():
    client = TestClient(app)
    original = client.post('/api/v1/projects', json={'name': 'Import Source'}).json()
    original_id = original['id']
    client.put(f'/api/v1/projects/{original_id}/scope', json={'in_scope_whitelist':['target.local'], 'out_of_scope_blacklist':[], 'max_rate_limit':10})
    client.post(f'/api/v1/projects/{original_id}/scope/lock')
    task = client.get(f'/api/v1/projects/{original_id}/tasks').json()[0]['tasks'][0]
    verification = client.post(f'/api/v1/projects/{original_id}/tasks/{task["id"]}/verify', json={'raw_content':'importable evidence /backup.zip'}).json()

    exported = client.get(f'/api/v1/projects/{original_id}/export')
    assert exported.status_code == 200
    imported = client.post('/api/v1/projects/import', files={'file': ('project.zip', exported.content, 'application/zip')})
    assert imported.status_code == 200, imported.text
    imported_id = imported.json()['project_id']
    assert imported_id != original_id

    project = client.get(f'/api/v1/projects/{imported_id}')
    assert project.status_code == 200
    assert project.json()['name'] == 'Import Source'
    evidence = client.get(f'/api/v1/projects/{imported_id}/evidence').json()
    assert len(evidence) == 1
    assert evidence[0]['evidence_id'].startswith('EVID-')
    content = client.get(f'/api/v1/projects/{imported_id}/evidence/{evidence[0]["evidence_id"]}/content')
    assert content.status_code == 200
    assert content.json()['content'] == 'importable evidence /backup.zip'
    report = client.get(f'/api/v1/projects/{imported_id}/report')
    assert report.status_code == 200
    assert 'Evidence Register & Integrity Log' in report.json()['markdown']


def test_import_rejects_zip_slip_member():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('../outside.txt', 'unsafe')
        archive.writestr('manifest.json', json.dumps({'format_version': '1.0'}))
    response = TestClient(app).post('/api/v1/projects/import', files={'file': ('unsafe.zip', buffer.getvalue(), 'application/zip')})
    assert response.status_code == 400


def test_import_export_round_trip_preserves_steps_and_mentor_messages():
    client = TestClient(app)
    original = client.post('/api/v1/projects', json={'name': 'Round Trip Steps Source'}).json()
    original_id = original['id']
    task = client.get(f'/api/v1/projects/{original_id}/tasks').json()[0]['tasks'][0]
    step = client.post(
        f'/api/v1/projects/{original_id}/tasks/{task["id"]}/steps',
        json={'title': 'Round trip checkpoint', 'objective': 'Verify export linkage.', 'why_it_matters': 'Keeps history.', 'completion_criteria': 'Step is preserved.', 'expected_evidence_type': 'TERMINAL_LOG'},
    ).json()
    client.post(f'/api/v1/projects/{original_id}/mentor/boss', json={'mode': 'summarize', 'user_message': 'Status check for export.'})

    exported = client.get(f'/api/v1/projects/{original_id}/export')
    assert exported.status_code == 200
    imported = client.post('/api/v1/projects/import', files={'file': ('project.zip', exported.content, 'application/zip')})
    assert imported.status_code == 200, imported.text
    imported_id = imported.json()['project_id']

    phases = client.get(f'/api/v1/projects/{imported_id}/tasks').json()
    imported_task = phases[0]['tasks'][0]
    assert [item['title'] for item in imported_task['steps']] == ['Round trip checkpoint']
    assert imported_task['steps'][0]['id'] != step['id']

    history = client.get(f'/api/v1/projects/{imported_id}/mentor/boss/history').json()
    assert [row['role'] for row in history] == ['user', 'assistant']
    assert history[0]['content'] == 'Status check for export.'
