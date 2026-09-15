"""Launch the workflow MCP server from any working directory."""
from __future__ import annotations
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
runpy.run_module("KB.mcp_workflow_server", run_name="__main__")
