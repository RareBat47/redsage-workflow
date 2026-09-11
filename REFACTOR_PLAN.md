# RedSage v2 — Refactor Plan

Principal engineer pass following the architecture audit. Scope is **high-impact, backwards-compatible** fixes only. `core/` remains frozen.

## Audit snapshot

| Area | Critical gaps found |
|------|---------------------|
| Architecture | `get_db()` runs full schema evolution every request; report vs archive task filters diverge; evidence router mixes verify + proposal policy |
| Quality | Raw `dict` on scope amend / task state; heavy frontend `any`; JSON-in-Text scope lists |
| Performance | Per-request `inspect`/`ALTER`; frontend `refresh()` fan-out |
| Security | No auth (loopback-by-convention only); finding confirm can rebind `evidence_id`; artifact size message drift; hardcoded API origin |

## Improvements (this pass)

### 1. Once-only database schema init (Performance / Architecture)

- [x] Gate `init_db()` behind a process-wide lock so schema work runs at most once
- [x] Call the gate from startup **and** `get_db()` (tests without lifespan still work)
- **Files:** `backend/database.py`, `backend/main.py`

### 2. Shared report task query (Correctness / Architecture)

- [x] Centralize “active (non-archived) tasks for reporting” loading
- [x] Use it from report preview/download **and** archive export snapshot
- **Files:** `backend/services/report_data.py` (new), `backend/routers/reports.py`, `backend/routers/archives.py`

### 3. Findings confirm + artifact limit hygiene (Security / Quality)

- [x] Reject confirm when draft already has a different `evidence_id` (409)
- [x] Unify artifact size error text to `MAX_ARTIFACT_BYTES`
- **Files:** `backend/routers/findings.py`, `backend/services/artifact_manager.py`
- **Tests:** `tests/test_findings_lifecycle.py` (extend), `tests/test_artifacts.py` (extend)

### 4. Pydantic DTOs for mutating endpoints (Quality / Validation)

- [x] Add `ScopeAmend` and `TaskStateUpdate` schemas
- [x] Wire `scope.amend` and `tasks.update_task_state` to those models
- **Files:** `backend/schemas/api_schemas.py`, `backend/routers/scope.py`, `backend/routers/tasks.py`

### 5. Loopback enforcement + relative API base (Security)

- [x] Middleware denying non-loopback clients by default (`REDSAGE_ALLOW_REMOTE=1` escape hatch; allow TestClient hosts)
- [x] Frontend API base: Vite dev keeps `127.0.0.1:8000`; production / same-origin uses `/api/v1` (override via `VITE_API_BASE`)
- **Files:** `backend/main.py`, `frontend/src/services/api.ts`
- **Docs:** `docs/SECURITY.md` updated for `REDSAGE_ALLOW_REMOTE`

## Out of scope (follow-ups)

- Full Alembic migration toolchain
- Evidence pipeline / proposal service split
- Frontend god-component decomposition / React Query
- Strict `tsconfig` + pinned npm versions
- Replacing JSON-in-Text scope columns

## Validation

- [x] `python -m pytest -m "not e2e" --tb=short -q` → **98 passed, 7 skipped, 1 deselected**
- [x] No project-level ruff/mypy/eslint config present; reliance on pytest contracts
- [x] Check off completed items above

## Result

All five planned improvements landed without regressions. Follow-ups remain intentional debt for a later pass.
