#!/usr/bin/env bash
# RedSage v2 dev-mode launcher (macOS/Linux)
# Starts the FastAPI backend and the Vite frontend dev server.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo "Starting backend: http://127.0.0.1:8000"
(cd "$ROOT" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000) &

echo "Starting frontend dev server: http://127.0.0.1:5173"
(cd "$ROOT/frontend" && npm run dev) &

echo ""
echo "Dev mode ready."
echo "  Backend  http://127.0.0.1:8000"
echo "  Frontend http://127.0.0.1:5173"
wait
