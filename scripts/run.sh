#!/usr/bin/env bash
# RedSage v2 prod-like local launcher (macOS/Linux)
# Serves the built frontend and the API from a single backend process.
# Run scripts/build.sh first if frontend/dist is missing.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$ROOT/frontend/dist/index.html" ]; then
  echo "Frontend build not found. Run scripts/build.sh first." >&2
  exit 1
fi

echo "RedSage v2 running at http://127.0.0.1:8000"
cd "$ROOT"
exec python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
