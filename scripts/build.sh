#!/usr/bin/env bash
# RedSage v2 frontend production build (macOS/Linux)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT/frontend"
npm run build
echo "Frontend build written to frontend/dist"
