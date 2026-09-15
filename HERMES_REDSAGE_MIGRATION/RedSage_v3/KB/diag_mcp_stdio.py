"""Raw JSON-RPC exchange with the engagement MCP server over stdio.

Bypasses the mcp SDK client so we can see exactly what the server writes back
and where it stalls.
"""
from __future__ import annotations

import json
import subprocess
import threading
import time

LAUNCHER = r"C:\Users\arifi\redsage-v3-engagement-mcp.cmd"
LOG = r"D:/HIGH LEVELS OF WORKS/RedSage_v3/data/kb_build/mcp_stderr.log"
PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)


def send(proc: subprocess.Popen, payload: dict) -> None:
    line = json.dumps(payload)
    proc.stdin.write(line + "\n")
    proc.stdin.flush()
    print(f"[sent] {line[:160]}", flush=True)


def main() -> int:
    started = time.perf_counter()
    with open(LOG, "w", encoding="utf-8") as errlog:
        proc = subprocess.Popen(
            ["cmd", "/c", LAUNCHER],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=errlog,
            text=True,
            bufsize=1,
        )
        responses: list[str] = []

        def reader() -> None:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                if line:
                    responses.append(line)
                    print(f"[recv] {line[:300]}", flush=True)

        threading.Thread(target=reader, daemon=True).start()

        send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "diag", "version": "1"},
            },
        })
        time.sleep(3)
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(proc, {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {
                "name": "generate_engagement_workflow",
                "arguments": {"problem_statement": PROBLEM, "top_k": 5},
            },
        })

        deadline = time.time() + 150
        while time.time() < deadline:
            if any('"id":2' in r or '"id": 2' in r for r in responses):
                break
            time.sleep(5)
            print(f"[wait] {time.perf_counter() - started:.0f}s, "
                  f"{len(responses)} message(s)", flush=True)

        answered = any('"id":2' in r or '"id": 2' in r for r in responses)
        print(f"[result] answered={answered} elapsed={time.perf_counter() - started:.1f}s",
              flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0 if answered else 1


if __name__ == "__main__":
    raise SystemExit(main())