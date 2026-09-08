import io
import json
import zipfile

from fastapi.testclient import TestClient
from backend.main import app

SECRET_PASSWORD = "Sup3rS3cret!Value"
SECRET_BEARER = "abcDEF1234567890TokenValueXYZ"
SECRET_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


def locked_project_with_evidence(client):
    project = client.post('/api/v1/projects', json={'name': 'Hardening Test'}).json()
    project_id = project['id']
    client.put(
        f'/api/v1/projects/{project_id}/scope',
        json={'in_scope_whitelist': ['target.local'], 'out_of_scope_blacklist': [], 'max_rate_limit': 10},
    )
    client.post(f'/api/v1/projects/{project_id}/scope/lock')
    task = client.get(f'/api/v1/projects/{project_id}/tasks').json()[0]['tasks'][0]
    raw = (
        f"password='{SECRET_PASSWORD}'\n"
        f"Authorization: Bearer {SECRET_BEARER}\n"
        f"token={SECRET_JWT}\n"
        "audit line /backup.zip"
    )
    verification = client.post(
        f'/api/v1/projects/{project_id}/tasks/{task["id"]}/verify', json={'raw_content': raw}
    )
    assert verification.status_code == 200
    return project_id


def test_redacted_excerpt_never_stores_known_secrets(monkeypatch):
    monkeypatch.delenv('CO_API_KEY', raising=False)
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    client = TestClient(app)
    project_id = locked_project_with_evidence(client)
    records = client.get(f'/api/v1/projects/{project_id}/evidence').json()
    excerpt = records[0]['redacted_excerpt']
    assert SECRET_PASSWORD not in excerpt
    assert SECRET_BEARER not in excerpt
    assert SECRET_JWT not in excerpt
    assert '[REDACTED_PASSWORD]' in excerpt
    assert 'Bearer [REDACTED_TOKEN]' in excerpt or '[REDACTED_JWT]' in excerpt


def test_export_db_rows_exclude_secrets_and_config(monkeypatch):
    monkeypatch.delenv('CO_API_KEY', raising=False)
    monkeypatch.delenv('COHERE_API_KEY', raising=False)
    client = TestClient(app)
    project_id = locked_project_with_evidence(client)
    exported = client.get(f'/api/v1/projects/{project_id}/export')
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        names = archive.namelist()
        assert not any('.env' in name.lower() or 'api_key' in name.lower() for name in names)
        data_text = archive.read('db/project_data.json').decode('utf-8')
        assert SECRET_PASSWORD not in data_text
        assert SECRET_BEARER not in data_text
        assert SECRET_JWT not in data_text
        assert any(name.startswith('artifacts/') for name in names)


def test_import_rolls_back_on_checksum_mismatch():
    client = TestClient(app)
    projects_before = len(client.get('/api/v1/projects').json())
    buffer = io.BytesIO()
    payload = json.dumps({
        'projects': [{'id': 'p-checksum', 'name': 'Checksum Fail', 'description': None, 'target_type': 'web_app', 'status': 'IN_PROGRESS', 'created_at': None}]
    }).encode('utf-8')
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('db/project_data.json', payload)
        archive.writestr('manifest.json', json.dumps({
            'format_version': '1.0',
            'checksums': [{'path': 'db/project_data.json', 'sha256': '0' * 64}],
        }))
    response = client.post('/api/v1/projects/import', files={'file': ('bad.zip', buffer.getvalue(), 'application/zip')})
    assert response.status_code == 400
    assert len(client.get('/api/v1/projects').json()) == projects_before


def test_env_template_and_gitignore_guard():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert (root / '.env.example').is_file()
    gitignore = (root / '.gitignore').read_text(encoding='utf-8').splitlines()
    assert any(line.strip() == '.env' for line in gitignore)
