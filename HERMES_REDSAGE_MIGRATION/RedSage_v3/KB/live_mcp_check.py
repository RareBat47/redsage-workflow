"""Exercise the registered engagement MCP server through a real MCP stdio client.

This spawns the same launcher Hermes uses, performs the MCP handshake,
lists tools, and invokes generate_engagement_workflow once with a real
authorized problem statement. It is an end-to-end check of the bounded
tool surface, not a unit test.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

LAUNCHER = Path("C:/Users/arifi/redsage-v3-engagement-mcp.cmd")

PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)


def _log(message: str) -> None:
    print(f"[check] {message}", flush=True)


async def _run() -> int:
    # asyncio's subprocess uses CreateProcess with shell=False, which cannot
    # run a .cmd directly — wrap it in cmd.exe explicitly.
    params = StdioServerParameters(command="cmd", args=["/c", str(LAUNCHER)])
    _log(f"spawning {params.command} {params.args}")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            _log("initializing session")
            await session.initialize()
            _log("session initialized")
            listed = await session.list_tools()
            names = [tool.name for tool in listed.tools]
            _log(f"tools: {names}")
            if "generate_engagement_workflow" not in names:
                print("LIVE_MCP_FAIL: expected tool not exposed")
                return 1
            _log("calling generate_engagement_workflow")
            result = await session.call_tool(
                "generate_engagement_workflow",
                {"problem_statement": PROBLEM, "top_k": 5},
            )
            _log("tool call returned")
            payload = result.content[0].text if result.content else ""
            data = json.loads(payload)
            roadmap = data.get("roadmap", {})
            summary = {
                "workflow_status": data.get("workflow_status"),
                "roadmap_status": roadmap.get("status"),
                "safety_decision": (roadmap.get("safety") or {}).get("decision"),
                "phase_count": len(roadmap.get("phases", [])),
                "retrieval_domains": roadmap.get("retrieval_domains"),
                "citation_count": len((data.get("roadmap_retrieval") or {}).get("citations", [])),
                "roadmap_receipt": roadmap.get("receipt_id"),
                "step_guidance": data.get("step_guidance") is not None,
                "evidence_review": data.get("evidence_review") is not None,
            }
            print(json.dumps(summary, indent=2))
            ok = (
                summary["workflow_status"] == "READY_FOR_REVIEW"
                and summary["phase_count"] > 0
                and summary["citation_count"] > 0
            )
            print("LIVE_MCP_OK" if ok else "LIVE_MCP_FAIL")
            return 0 if ok else 1


async def main() -> int:
    try:
        return await asyncio.wait_for(_run(), timeout=240)
    except asyncio.TimeoutError:
        print("LIVE_MCP_FAIL: timed out after 240s")
        return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))