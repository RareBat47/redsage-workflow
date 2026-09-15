"""Test whether running the workflow on a worker thread (as FastMCP does)
is what makes the call hang, versus the same call on the main thread.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time

PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)

from KB.engagement_workflow import run_internal_engagement_workflow  # noqa: E402


def _call(label: str) -> dict:
    started = time.perf_counter()
    result = run_internal_engagement_workflow(PROBLEM, top_k=5)
    print(f"[{label}] finished in {time.perf_counter() - started:.2f}s "
          f"thread={threading.current_thread().name}", flush=True)
    return result


async def main() -> int:
    print("[diag] main-thread call", flush=True)
    t = time.perf_counter()
    try:
        await asyncio.wait_for(asyncio.to_thread(_call, "to_thread"), timeout=180)
        print(f"[diag] to_thread total {time.perf_counter() - t:.2f}s", flush=True)
    except asyncio.TimeoutError:
        print(f"[diag] to_thread HUNG (>{time.perf_counter() - t:.0f}s)", flush=True)
        return 2

    print("[diag] second to_thread call (warm)", flush=True)
    t = time.perf_counter()
    try:
        result = await asyncio.wait_for(asyncio.to_thread(_call, "to_thread-2"), timeout=60)
        print(f"[diag] to_thread-2 total {time.perf_counter() - t:.2f}s", flush=True)
    except asyncio.TimeoutError:
        print("[diag] to_thread-2 HUNG", flush=True)
        return 3

    print(json.dumps({
        "workflow_status": result.get("workflow_status"),
        "phase_count": len((result.get("roadmap") or {}).get("phases", [])),
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))