#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export DATABASE_URL="sqlite:///$ROOT/data/verify_all.db"
export CO_API_KEY=""
export COHERE_API_KEY=""

python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"
node --version
python3 -m compileall -q backend
python3 -m pytest -m 'not e2e' -q
(cd frontend && npm ci && npm run build)
python3 -m playwright install chromium
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 >/tmp/redsage-e2e.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
python3 - <<'PY'
import time
import urllib.request
for _ in range(60):
    try:
        if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=1).status == 200:
            break
    except Exception:
        time.sleep(0.5)
else:
    raise SystemExit('RedSage server did not become ready')
PY
python3 -m pytest -m e2e -q
python3 -c "from backend.database import SessionLocal; from backend.services.recovery_service import reconcile_storage_and_db; print(reconcile_storage_and_db(SessionLocal()))"
