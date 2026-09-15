#!/usr/bin/env bash
set -euo pipefail
REDSAGE_V2_ROOT="${REDSAGE_V2_ROOT:-$HOME/projects/RedSage_v2}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$REDSAGE_V2_ROOT"
exec "$PYTHON_BIN" -m interfaces.mcp_server
