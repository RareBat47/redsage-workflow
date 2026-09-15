#!/usr/bin/env bash
set -euo pipefail
REDSAGE_V3_ROOT="${REDSAGE_V3_ROOT:-$HOME/projects/RedSage_v3}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$REDSAGE_V3_ROOT"
exec "$PYTHON_BIN" -m KB.assessment_mcp_server
