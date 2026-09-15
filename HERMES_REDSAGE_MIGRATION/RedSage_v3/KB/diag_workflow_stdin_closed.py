"""Run the engagement workflow with stdin closed, mimicking the MCP child."""
from __future__ import annotations

import json
import sys
import time

print("[t] importing workflow", flush=True)
from KB.engagement_workflow import run_internal_engagement_workflow  # noqa: E402

print(f"[t] stdin isatty={sys.stdin.isatty()}", flush=True)
started = time.perf_counter()
result = run_internal_engagement_workflow(
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization.",
    top_k=5,
)
elapsed = time.perf_counter() - started
print(f"[t] workflow finished in {elapsed:.2f}s", flush=True)
print(json.dumps({
    "workflow_status": result.get("workflow_status"),
    "phase_count": len((result.get("roadmap") or {}).get("phases", [])),
}, indent=2), flush=True)