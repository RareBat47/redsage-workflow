"""A/B the MCP client with stderr drained vs not drained.

diag_mcp_transport (errlog drained) returned in ~41s; live_mcp_check (no
errlog) times out at 240s. Test that single variable.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LAUNCHER = r"C:\Users\arifi\redsage-v3-engagement-mcp.cmd"
PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)


async def probe(label: str, drain_stderr: bool, timeout: float) -> dict:
    params = StdioServerParameters(command="cmd", args=["/c", LAUNCHER])
    started = time.perf_counter()
    outcome = {"label": label, "drain": drain_stderr}

    async def _run() -> dict:
        if drain_stderr:
            with open(f"data/kb_build/mcp_ab_{label}.log", "w", encoding="utf-8") as log:
                async with stdio_client(params, errlog=log) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        await session.list_tools()
                        result = await session.call_tool(
                            "generate_engagement_workflow",
                            {"problem_statement": PROBLEM, "top_k": 5},
                        )
                        return json.loads(result.content[0].text)
        else:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    await session.list_tools()
                    result = await session.call_tool(
                        "generate_engagement_workflow",
                        {"problem_statement": PROBLEM, "top_k": 5},
                    )
                    return json.loads(result.content[0].text)

    try:
        payload = await asyncio.wait_for(_run(), timeout=timeout)
        outcome["status"] = "ok"
        outcome["workflow_status"] = payload.get("workflow_status")
        outcome["phases"] = len((payload.get("roadmap") or {}).get("phases", []))
    except asyncio.TimeoutError:
        outcome["status"] = "timeout"
    except Exception as error:  # noqa: BLE001
        outcome["status"] = f"error: {type(error).__name__}: {error}"
    outcome["elapsed_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(outcome), flush=True)
    return outcome


async def main() -> int:
    await probe("drained", True, 120)
    await probe("undrained", False, 120)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))