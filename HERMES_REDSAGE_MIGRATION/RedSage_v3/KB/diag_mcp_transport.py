"""Probe whether the MCP client transport is what stalls, not the workflow."""
from __future__ import annotations

import asyncio
import json
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LAUNCHER = r"C:\Users\arifi\redsage-v3-engagement-mcp.cmd"
LOG = r"D:/HIGH LEVELS OF WORKS/RedSage_v3/data/kb_build/mcp_errlog_probe.log"
PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)


async def main() -> int:
    params = StdioServerParameters(command="cmd", args=["/c", LAUNCHER])
    print(f"[probe] spawning {params.command} {params.args}", flush=True)
    started = time.perf_counter()
    with open(LOG, "w", encoding="utf-8") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            print(f"[probe] transport up at {time.perf_counter() - started:.1f}s", flush=True)
            async with ClientSession(read, write) as session:
                await session.initialize()
                print(f"[probe] initialized at {time.perf_counter() - started:.1f}s", flush=True)
                listed = await session.list_tools()
                print(f"[probe] tools={[t.name for t in listed.tools]} at {time.perf_counter() - started:.1f}s", flush=True)
                print("[probe] calling tool", flush=True)
                result = await session.call_tool(
                    "generate_engagement_workflow",
                    {"problem_statement": PROBLEM, "top_k": 5},
                )
                print(f"[probe] tool returned at {time.perf_counter() - started:.1f}s", flush=True)
                payload = json.loads(result.content[0].text)
                print(json.dumps({
                    "workflow_status": payload.get("workflow_status"),
                    "phase_count": len((payload.get("roadmap") or {}).get("phases", [])),
                }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))