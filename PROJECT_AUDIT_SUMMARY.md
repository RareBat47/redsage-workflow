# RedSage v2 — Project Audit Summary

**Audit date:** 2026-09-11
**Method:** Direct source inspection. Code is treated as truth over documentation. Every claim below cites a file and, where useful, a line reference. The regenerated `EXPLANATION.md` (same date) was used as the cross-check document; where the two disagree, the code wins and the divergence is recorded.
**Scope:** `backend/` (application), `frontend/src/`, `core/`, `interfaces/`, `data/methodologies/`, `tests/`, configuration.
**Test evidence:** `python -m pytest -m "not e2e"` → **83 passed, 7 skipped, 1 deselected** (91 collected). Skips are the 7 credential-gated live-AI benchmark tests; the deselected item is the Playwright browser suite.

---

## 1. Corrections from Previous Audit

The previous edition of this document contained at least two factual errors. Both were re-verified by direct inspection and are now corrected.

### Correction 1 — Proposal approval phase targeting

- **Previous (wrong) claim:** proposal approval locates its destination phase with `Phase.name.like("%Phase 4%")`.
- **Verified fact:** approval uses an **exact, project-scoped, active-phase match** on `Phase.name == proposal.phase_name`.
- **Evidence:** `backend/routers/proposals.py:18-24`:

```python
phase = db.query(Phase).filter(
    Phase.project_id == project_id,
    Phase.name == proposal.phase_name,
    Phase.is_archived.is_(False),
).first()
if not phase:
    raise HTTPException(400, f"No target phase is available for proposed tasks: no active phase named '{proposal.phase_name}' in this project")
```

- **Search result:** the string `LIKE` does not appear in any phase lookup in the codebase. A non-Phase-4 approval is covered by `tests/test_methodology_seeding.py::test_proposal_approval_honors_non_phase_four_target`, and the unknown-phase path by `test_proposal_approval_rejects_unknown_target_phase_without_creating_task` and `test_proposal_approval_error_names_the_missing_phase`.

### Correction 2 — Mentor messages in archive export/import

- **Previous (wrong) claim:** `mentor_messages` are "not covered by archive export/import".
- **Verified fact:** mentor messages are **exported and imported with full ID remapping**.
- **Evidence:**
  - Export collects them (`archives.py:52`) and serializes them into `db/project_data.json` under the `mentor_messages` key with fields `id, project_id, task_id, step_id, mode, role, content, ai_available, created_at` (`archives.py:72`).
  - Import builds an ID map (`archives.py:181`) and inserts remapped rows, mapping `task_id`/`step_id` through the corresponding maps (`archives.py:204-205`).
- **Test evidence:** `tests/test_import_archive.py::test_import_export_round_trip_preserves_steps_and_mentor_messages` asserts the round-tripped project's boss history returns `["user", "assistant"]` with preserved content.

### Correction 3 — Structural drift (silent, not previously flagged)

The earlier edition also understated the system's size. Corrected:

| Claim | Previous | Actual (verified) |
|---|---|---|
| Routers | 12 | **15** |
| API operations | not stated | **42** across those routers |
| Runtime migration blocks | 2 | **7** |
| Database tables | not stated | **12** |

Evidence: `backend/main.py:5,11` (15 router imports/includes); OpenAPI dump of `backend.main:app` (42 operations); `backend/database.py:26-64` (7 logical `ALTER` groups); `backend/models/schema.py` (12 `__tablename__` declarations).

---

## 2. System Under Audit

| Aspect | Verified state |
|---|---|
| Architecture | FastAPI backend + SQLite + per-project artifact directory + React/Vite SPA (single `App` component, no router library) |
| Entry point | `backend/main.py` (`app`, version `2.0.0-mvp`), all routes under `/api/v1` |
| Auth | **None.** Single-operator, loopback-only design |
| Scope enforcement | Whitelist/blacklist + lock. Verification refused (400) while unlocked; non-whitelisted `target_host` rejected (422) |
| Execution model | None. `command_template` strings are display-only; no route executes anything |
| AI surfaces | 5: verifier, task/Step mentor, planner, refiner, boss mentor. Each has an offline path and a failure path |
| Persistence of AI chat | Yes — `mentor_messages` (task/Step scope and project scope) |
| Workflow mutation | Only via explicit human action (`/workflow/apply`, proposal approve) |

---

## 3. Verified Findings by Area

### 3.1 Data model and storage — Pass

- 12 tables confirmed: `projects`, `scopes`, `scope_amendments`, `audit_events`, `phases`, `tasks`, `task_steps`, `assets`, `evidence`, `findings`, `workflow_proposals`, `mentor_messages`.
- `projects.brief` is nullable (`schema.py:11`); migration block 3 adds it to legacy DBs (`database.py:34-37`).
- `task_steps` exists with full objective/why/criteria/evidence-type/status/order/archive/justification fields (`schema.py:92-109`).
- `evidence.task_id` remains **mandatory**; `evidence.step_id` is nullable (`schema.py:124-125`).
- `evidence.raw_content` is legacy-only and never written by current code (comment at `schema.py:126`; verifier writes to disk and stores metadata).
- **`create_all()` runs before the reflection block** (`database.py:24-26`), so fresh databases cannot fail on missing-table reflection.
- SQLite has **no foreign-key enforcement enabled**; parentage is enforced in application code at each route. This is consistent, but it means DB-level referential integrity is not a backstop.

### 3.2 Migrations — Pass (with one operational note)

Seven logical migration blocks, all idempotent and reflection-guarded:

1. `workflow_proposals.created_task_id` · 2. `assets.source_task_id` · 3. `projects.brief` · 4. `evidence.step_id` · 5. `phases` archive metadata · 6. `tasks` archive metadata · 7. `task_steps` archive metadata.

Operational note (also §6.3 item 5): `init_db()` is invoked from `get_db()` on **every request**, so `create_all()` plus all seven blocks execute per request. It is correct but wasteful.

### 3.3 API surface — Pass

- 42 operations across 15 routers, confirmed by dumping `app.openapi()["paths"]`.
- The canonical route-contract test (`tests/test_api_contracts.py`) asserts the presence of the workflow, digest, boss-mentor, Step, and brief routes.
- Error-code discipline observed and tested: 400 (locked scope, justification, proposal cap, missing phase), 404 (parentage), 409 (Step-bearing completion and verification, archived Step mutation, completed-task Step creation), 422 (schema/validation).

### 3.4 Evidence and verification — Pass

- Artifact write is atomic: temp file → `flush` → `fsync` → `os.replace` → best-effort dir fsync, with temp cleanup (`artifact_manager.py:44-61`).
- SHA-256 is computed over the exact bytes written (`artifact_manager.py:62`).
- Clipping (80 lines) precedes redaction inside `verify_task_evidence`, and both precede any provider call (`cohere_service.py:128-132`). Redaction covers 10 pattern families and re-processes a URL-decoded copy (`cohere_service.py:23-34, 65-76`).
- **Offline verdict is `AMBIGUOUS`/`LOW` and cannot complete work** (`cohere_service.py:101-110`); the provider-failure path is also `AMBIGUOUS`/`LOW` (`cohere_service.py:113-125`); both are covered by `tests/test_cohere_resilience.py`.
- Verdict→state mapping is centralized in `verify_and_persist_evidence` (`evidence.py:69-75`): only `PASS` completes; `CONFIRMED_NEGATIVE` sets status plus justification.
- **Task-level verification is disabled (409) once a task has active Steps** (`evidence.py:142-143`), preventing two parallel sources of truth; covered by `tests/test_task_steps.py`.
- The Step verify route delegates to the same helper with `step=` (`task_steps.py:117-131`), so one code path serves both levels.

### 3.5 Steps and rollup — Pass

- One shared state machine for tasks and Steps (`backend/services/task_state.py`): same five statuses, same ≥ 5-char justification rule, same audit shape (`TASK_STATE_CHANGED` with `entity_type="task_step"`).
- Rollup fires only when a task has ≥ 1 active Step **and** all active Steps are terminal (`task_state.py:39-54`); it writes a Task-level audit event. Zero-Step tasks retain the legacy direct-transition behavior.
- Archive filtering is consistent in `GET /tasks`, readiness, digest, and Step listing.

### 3.6 AI planner — Pass

- Canonical phase list is loaded from `data/methodologies/baseline_methodology.json` via `canonical_phase_names()`; no duplicated list exists (`planner_service.py:73-74`).
- `WorkflowDraft` enforces exactly 7 phases in canonical order (`planner_service.py:50-61`).
- The clarification gate runs **before** both the live path and the offline fallback (`planner_service.py:120-126`), so no draft is produced from an incomplete brief even without a key.
- Offline and provider-failure paths both return the baseline reshape with one Step per task (`planner_service.py:89-110, 140-141`).
- Command templates from the model are rejected if they contain `exploit`, `payload`, `reverse shell`, or `meterpreter` (`planner_service.py:36-41`).
- Apply is transactional with rollback on error, and Replace **archives in place** (`workflow_engine.py:69-80`) rather than deleting, preserving `evidence.task_id`/`step_id` links (`tests/test_planner_workflow.py`).

### 3.7 Refiner and proposal phase selection — Pass (after a fixed defect)

- The Refiner returns a `phase_name` that is validated against the canonical list; anything else becomes `Phase 4: Vulnerability Analysis` (`asset_proposal_service.py:24-25`).
- No-key mode returns a deterministic Phase-4 proposal (`asset_proposal_service.py:43-44`).
- **Previously fixed defect (still guarded):** an empty or fully-invalid provider list could yield zero proposals; `suggest_safe_tasks` now falls back to the deterministic proposal (`asset_proposal_service.py:52-55`), and the keyword call site is also null-guarded (`evidence.py:96-103`). Regression tests: `test_refiner_empty_response_falls_back_to_standard_proposal`, `test_keyword_discovery_never_500s_when_refiner_returns_empty`.
- Phase propagation into the keyword trigger is covered end-to-end by `tests/test_assets_pivot.py::test_keyword_discovery_uses_ai_selected_phase` (Phase 5 stored and approved into Phase 5).

### 3.8 Mentor persistence — Pass

- Both mentor routes write a user turn and an assistant turn per successful call (`mentor.py:41-59`, `workflow_digest.py:37-38`).
- User content is redacted and clipped before storage (`mentor.py:40`); assistant turns store the fallback availability flag.
- Task/Step threads filter on `task_id` plus `step_id` (including `IS NULL` for task scope) and Boss threads filter on both being null, keeping the two thread families distinct (`mentor.py:80-84`, `workflow_digest.py:48-52`).
- Audit events record mode, availability, and question length only — never content (`mentor.py:60-66`).
- Context is bounded at 8,000 characters at serialization time (`mentor_service.py:152-153`).

### 3.9 Archive engine — Pass

- Zip-slip and expansion hardening is thorough: member path normalization, absolute/backslash/`.`/`..` rejection, 100 MB archive cap, 10 MB member cap, 1,000-member cap, cumulative expansion cap, single-project requirement, required-member presence, and per-member checksum verification (`archive_service.py:24-69`, `archives.py:137-156`).
- Import remaps every entity, including Steps and mentor messages, and rolls back plus deletes the new artifact directory on failure (`archives.py:159-216`).
- Mentor messages are included (Correction 2).

### 3.10 Frontend — Pass (with notes)

- Single `App` component with a 5-value `View` union; new panels (`ProjectBriefPanel`, `WorkflowPlannerPanel`, `TaskStepsPanel`, `BossBrainPanel`) are wired into it.
- Mentor history is API-loaded; no in-memory conversation Map remains as a source of truth.
- Planner drafts are rendered from the response and never mutate the roadmap before Apply.
- Evidence library search matches Step titles when present.
- Note: the API base URL is hardcoded to `127.0.0.1:8000` (`services/api.ts:3`), consistent with the app's single-machine design.

### 3.11 Auxiliary KB subsystem — Pass, unmaintained by the app

- `core/` is importable standalone, has no web/LLM dependencies in the retrieval path, and preserves the original embedding algorithm needed to read existing ChromaDB vectors.
- `interfaces/` exposes read-only MCP tools.
- Neither is referenced by `backend/` or the frontend. `data/chroma/` is preserved data.

---

## 4. Documentation Cross-Check Against the New EXPLANATION.md

| # | Claim in `EXPLANATION.md` (2026-09-11) | Independent verification | Status |
|---|---|---|---|
| 1 | 15 routers / 42 operations | OpenAPI dump | Match |
| 2 | 12 tables | `Base.metadata.tables` | Match |
| 3 | 7 migration blocks | `database.py:26-64` | Match |
| 4 | Exact phase approval, no `LIKE` | `proposals.py:18-24`; repo-wide search | Match |
| 5 | `mentor_messages` in export/import with remapping | `archives.py:52,72,181,204-205` + round-trip test | Match |
| 6 | Offline verifier `AMBIGUOUS`, no auto-complete | `cohere_service.py:101-110`; resilience tests | Match |
| 7 | Step rollup + 409 guards | `task_state.py`, `tasks.py:44-45`, `evidence.py:142-143` | Match |
| 8 | Digest coverage uses the same helper as readiness | `readiness_service.py`; both callers | Match |
| 9 | Planner clarification gate precedes offline fallback | `planner_service.py:120-126` | Match |
| 10 | Archive limits 100 MB / 10 MB / 1,000 members / v1.0 | `archive_service.py:15-17,44-69` | Match |
| 11 | Readiness formula `100 − 30×critical − 10×warning`, export requires 0 critical | `reports.py:40-43` | Match |
| 12 | Mentor context hard cap 8,000 chars | `mentor_service.py:152-153` | Match |

No contradictions were found between the regenerated `EXPLANATION.md` and the code during this cross-check.

---

## 5. New Discrepancies Found in This Audit

Beyond Corrections 1–3, the following were discovered during inspection and are recorded in both this audit and `EXPLANATION.md §8.3`.

| # | Severity | Finding | Evidence |
|---|---|---|---|
| D1 | Low | `artifact_manager.read_artifact()` reports a **5 MB** limit in its error text but enforces the 10 MB `MAX_ARTIFACT_BYTES` constant. The enforced limit is 10 MB. | `artifact_manager.py:13,80` |
| D2 | Medium | **Report matrix inconsistency.** The live report endpoints include archived tasks in the methodology matrix; the exported report snapshot excludes them. Archived-task treatment is therefore undefined rather than specified. | `reports.py:11` vs `archives.py:86` |
| D3 | Low | **Port collision.** `interfaces/api.py` defaults to `127.0.0.1:8000`, the same port as the main app; both cannot run on defaults simultaneously. | `interfaces/api.py:86`, `backend/main.py` |
| D4 | Low | **Unpinned frontend dependencies.** `package.json` declares every dependency as `"latest"` with no committed lockfile, so builds are not reproducible. | `frontend/package.json` |
| D5 | Low (perf) | `get_db()` invokes `init_db()` per request, running `create_all()` plus seven reflection/DDL blocks each time. | `database.py:12-20` |
| D6 | Low | `planner_service` imports `cohere` at module import time and is transitively imported by `projects.py`, making `cohere` a hard import-time dependency even for fully offline operation. | `planner_service.py:8`; `workflow_engine.py:6`; `projects.py:8` |
| D7 | Info | `mentor_service.build_context_pack()` raises `ValueError("Step not found")` for an invalid Step, but all callers pre-validate, so the branch is unreachable in the current call graph. | `mentor_service.py:94-96` |
| D8 | Low | `POST /findings/{id}/confirm` **replaces** the stored `evidence_id` with the payload value instead of verifying equality, so a confirmation can silently re-point a draft's evidence link. | `findings.py:69` |
| D9 | Info | Asset-suggestion title dedup includes **archived** task titles and all historical proposal titles, so a title can be permanently blocked from re-proposal. | `assets.py:29-30` |
| D10 | Info (test hygiene) | The non-E2E suite writes real rows and artifacts into the configured database (`data/redsage.db`, `data/projects/`); repeated runs accumulate data. | `database.py:7`; observed 1,200+ residual projects during smoke testing |

None of D1–D10 are exploitable or data-losing. D2 and D8 are behavioral inconsistencies worth a product decision; the remainder are hygiene items.

---

## 6. Test & Verification Status

**Command executed for this audit:**

```
python -m pytest -m "not e2e"
```

**Result (actual, current):**

| Metric | Count |
|---|---|
| Collected | 91 |
| Deselected (marker `e2e`) | 1 |
| Selected | 90 |
| **Passed** | **83** |
| **Skipped** | **7** |
| **Failed** | **0** |
| Warnings | 230 (deprecations only: FastAPI `on_event`, `datetime.utcnow`, Vite config loader, third-party Cohere/Pydantic) |

- Skips: the 7 credential-gated tests in `tests/test_live_ai_benchmark.py`.
- Deselected: `tests/e2e/test_browser_suite.py` (Playwright; requires a running server and Chromium).
- Supporting gate: `python -m compileall backend` → clean; `npm run build` in `frontend/` → success (36 modules, only the pre-existing Vite config-loader warning).

Test files touching the areas corrected above, all passing: `test_assets_pivot.py` (7), `test_methodology_seeding.py` (7), `test_workflow_history.py` (1), `test_task_steps.py` (8), `test_mentor.py` (7), `test_planner_workflow.py` (6), `test_boss_brain.py` (5), `test_import_archive.py` (3), `test_cohere_resilience.py` (3).

---

## 7. Risk Register (current)

| Risk | Rating | Mitigation in place | Residual |
|---|---|---|---|
| No auth on API | High if exposed | Designed for loopback single operator; CORS limited to local Vite origins | Do not bind to a routable interface without adding auth |
| Live provider key on disk (`.env`) | Medium | Gitignored; excluded from archives | Travels with folder copies; rotate for distribution |
| Archived-task treatment inconsistent in reports (D2) | Medium | None | Define intended behavior and align `reports.py`/`archives.py` |
| Finding evidence re-pointing (D8) | Low–Medium | Evidence must exist and belong to the project | Consider validating equality or auditing the change |
| Unpinned frontend deps (D4) | Medium for reproducibility | None | Commit a lockfile |
| Per-request migrations (D5) | Low | Idempotent by construction | Move to startup-only if latency matters |
| Test runs pollute the dev DB (D10) | Low | None | Use a dedicated test database |

---

## 8. Verdict

The system is internally consistent with its constitutional constraints: no execution, no exploit content, human approval for every AI-authored workflow change, evidence-gated findings, deterministic offline degradation on every AI surface, and no silent data loss on provider failure. The two previously published false claims are corrected with code evidence, and the corrected structural figures (15 routers / 42 operations / 12 tables / 7 migration blocks) are reproducible from the commands recorded in §6.

The remaining items are hygiene and behavior-definition issues (D1–D10), not regressions. D2 and D8 are the only findings that could change reported content or traceability and should be resolved by explicit product decision.
