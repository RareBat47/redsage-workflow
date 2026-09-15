# Hermes Provider Probe Cookbook

## Purpose

Provide copy-ready templates for validating provider health and model acceptance before changing Hermes runtime routing.

## 1) Chat completion probe

```bash
python - <<'PY'
import json
import urllib.request
import urllib.error

ENDPOINT = 'https://api.xkiro.com/v1'
MODEL = 'openai/gpt-5.3-codex-spark'
API_KEY = 'env:KEY_NAME'  # replace with env lookup logic in runtime

req = urllib.request.Request(f'{ENDPOINT}/chat/completions')
req.add_header('Authorization', f'Bearer {API_KEY}')
req.add_header('Content-Type', 'application/json')

body = {
    'model': MODEL,
    'messages': [{'role': 'user', 'content': 'ping'}],
    'max_tokens': 5,
}

try:
    with urllib.request.urlopen(req, data=json.dumps(body).encode(), timeout=20) as r:
        print('HTTP', r.status)
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code)
    print(exc.read().decode()[:240])
except Exception as exc:
    print(type(exc).__name__, exc)
PY
```

## 2) Models catalog probe

```bash
python - <<'PY'
import json
import urllib.request

ENDPOINT = 'https://api.xkiro.com/v1'
API_KEY = 'env:KEY_NAME'

req = urllib.request.Request(f'{ENDPOINT}/models')
req.add_header('Authorization', f'Bearer {API_KEY}')

try:
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
        print('models', len(data.get('data', [])))
except Exception as exc:
    print(type(exc).__name__, exc)
PY
```

## 3) Interpretation quick map

- `HTTP 200`: model + transport generally healthy.
- `HTTP 401/403`: key scope/credential issue.
- `HTTP 404` on model: wrong model ID or unsupported provider slug.
- `HTTP 429`: quota/rate or policy pressure.
- `HTTP 503` / `service_unavailable` / `overload`: upstream provider instability.
- Re-run after 60–120s if overload appears bursty.

## 4) Follow-up in Hermes

- `hermes config get model`
- `hermes fallback list`
- `hermes logs errors --since 30m --level WARNING`
- `hermes -z "reply only: ok"`
