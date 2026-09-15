# RedSage v2 — Active Progress

Historical receipts are archived at `docs/internal/archive/PROGRESS-20260912-and-earlier.md`.

## Current product state

- Workflow Generation Initiative (0A, G0–G6, FINAL): **complete**.
- Current source-of-truth documents: `EXPLANATION.md` and `docs/USER_MANUAL.md`.
- No active product milestone is approved in this file.

## Hermes blueprint rollout — complete (2026-09-13)

Implemented the supplied `Downloads/RedSage-Begins.md` context layer:

- Created `SOUL.md` and `AGENTS.md`.
- Added eight project runbooks in `skills/` and the optional documentation-reconciliation runbook.
- Added `docs/internal/HERMES_CONTEXT_SUMMARY.md`, `HERMES_MCP_CONFIG.md`, and `KB_COMPLIANCE_NOTES.md`.
- Added the native `redsage-kb` MCP server using the project venv and workspace CWD.
- Enabled mandatory `kb_search` before a RedSage domain-entity implementation claim or code change; KB output remains untrusted and may only support safe, cited methodology guidance.

## Latest verification — 2026-09-13

| Check | Result |
|---|---|
| `hermes mcp test redsage-kb` | PASS — connected; `kb_search`, `kb_sources`, and `kb_stats` discovered |
| `.venv/Scripts/python.exe -m compileall backend` | PASS |
| `.venv/Scripts/python.exe -m pytest -m "not e2e" -q -p no:cacheprovider -rs` | PASS — 101 passed, 7 skipped, 1 deselected |
| `npm run build` in `frontend/` | PASS — existing Vite `configLoader: native` warning remains |
| `core/**`, `data/chroma/**` | No changes |

### Test telemetry explanation

- The **one deselected test** is intentional: `tests/e2e/test_browser_suite.py::test_full_magic_demo_flow`, marked `@pytest.mark.e2e`, excluded by the explicit `-m "not e2e"` gate.
- The **seven skipped tests** are the live Cohere benchmark scenarios in `tests/test_live_ai_benchmark.py`; their declared skip reason is missing `CO_API_KEY` / `COHERE_API_KEY`. They are opt-in live-provider tests, not silently broken tests.

## Operating decisions

1. Preserve existing uncommitted product changes; do not overwrite them unless explicitly scoped.
2. KB compliance cadence: monthly plus pre-demo.
3. `interfaces/` remains restricted to MCP integration unless explicitly expanded.
4. E2E stays explicit-request only.
5. Durable storage for `data/redsage.db` and `data/projects/` remains an operational item to verify.

## Next action

Start a fresh Hermes session from `D:/HIGH LEVELS OF WORKS/RedSage_v2` to load the project context and enabled `redsage-kb` MCP tools. Before the next domain-model/code task, query `kb_search` and then follow the incremental-ticket skill.
