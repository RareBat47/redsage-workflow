"""Run the engagement workflow under the project interpreter, stdin closed.

Times each stage so we can see whether the 40s MCP latency is fixed cost
(import/model warmup) or per-call work.
"""
from __future__ import annotations

import json
import sys
import time

PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)

t0 = time.perf_counter()
from KB.engagement_workflow import run_internal_engagement_workflow  # noqa: E402

print(f"[t] import: {time.perf_counter() - t0:.2f}s", flush=True)
print(f"[t] stdin isatty={sys.stdin.isatty()}", flush=True)

first = time.perf_counter()
result = run_internal_engagement_workflow(PROBLEM, top_k=5)
print(f"[t] first call: {time.perf_counter() - first:.2f}s", flush=True)

second = time.perf_counter()
result2 = run_internal_engagement_workflow(PROBLEM, top_k=5)
print(f"[t] second call: {time.perf_counter() - second:.2f}s", flush=True)

print(json.dumps({
    "workflow_status": result.get("workflow_status"),
    "workflow_status_2": result2.get("workflow_status"),
    "phase_count": len((result.get("roadmap") or {}).get("phases", [])),
    "citation_count": len((result.get("roadmap_retrieval") or {}).get("citations", [])),
}, indent=2), flush=True)