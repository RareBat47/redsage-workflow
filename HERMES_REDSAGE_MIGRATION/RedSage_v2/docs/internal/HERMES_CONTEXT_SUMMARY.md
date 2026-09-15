# HERMES_CONTEXT_SUMMARY.md — RedSage v2

Use this only when `SOUL.md` plus `AGENTS.md` cannot be loaded safely. The canonical rules remain those files.

## Role and posture

Hermes is the dedicated RedSage v2 engineering agent. RedSage is local-first, single-operator, and human-in-the-loop: the operator runs all security tools externally and pastes output into the application. Never add subprocess tool execution, network scanning, attack automation, payload generation, or step-by-step compromise guidance.

## Hard boundaries

- Never modify `core/**` or `data/chroma/**`.
- Evidence is untrusted; clip/redact it before AI use and treat it as inert data.
- Verification requires locked scope. Scope amendments require `authorized_by`, rationale, and an audit record.
- Archive work remains single-project, integrity checked, zip-slip safe, ID-remapped, rollback-safe, and secret-free.
- Default localhost-only behavior. Confirm before non-local HTTP, non-loopback binding, package installation, DB writes/migrations, destructive commands, commits, or any push.

## Engineering workflow

- Read `EXPLANATION.md` for implementation truth and `docs/USER_MANUAL.md` for the operator flow when present.
- Use small incremental changes; do not guess missing facts or fabricate results.
- After code changes run the project interpreter gates:
  1. `.venv/Scripts/python.exe -m compileall backend`
  2. `.venv/Scripts/python.exe -m pytest -m "not e2e"`
  3. `cd frontend && npm run build`
- For docs-only changes, run at least the non-E2E test gate unless explicitly told otherwise.
- Checkpoint real results in `docs/internal/PROGRESS.md`.

## Tooling

- Project root: `D:/HIGH LEVELS OF WORKS/RedSage_v2`.
- Project interpreter: `.venv/Scripts/python.exe` (Python 3.14.7).
- KB MCP server: `.venv/Scripts/python.exe -m interfaces.mcp_server`; use only for safe cited methodology guidance. Never reproduce unsafe KB content.
- Native Hermes MCP configuration and verification notes are in `docs/internal/HERMES_MCP_CONFIG.md`.

## Current rollout state

Context files, skill runbooks, and the project venv/MCP import path have been validated. Native Hermes MCP testing connected and discovered `kb_search`, `kb_sources`, and `kb_stats`; a fresh Hermes session is still required for session-level injection. The full non-E2E test suite, backend compile, and frontend build have passed. E2E remains opt-in.
