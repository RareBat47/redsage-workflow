# RedSage v2 Milestone Progress

## Workflow Generation Initiative

### Milestone 0A: ADR-3 Exact Proposal Targeting — COMPLETE (2026-09-10)

Implemented the first required product-code change from the revised plan. Proposal approval now resolves `Phase.name == proposal.phase_name` within the requested project instead of using a Phase 4 `LIKE` lookup. Missing target phases return HTTP 400 and do not create a Task. Existing Phase 4 approval, audit, undo, and asset-proposal behavior remains intact.

Files changed:
- `backend/routers/proposals.py`
- `tests/test_methodology_seeding.py`

Tests added:
- Approval of a proposal targeting `Phase 2: Intelligence Gathering` lands in Phase 2 and not Phase 4.
- Approval of a proposal targeting an unknown phase returns 400 and leaves the Task count unchanged.

Commands run and results:
- `python -m pytest tests/test_methodology_seeding.py tests/test_workflow_history.py tests/test_assets_pivot.py -v` -> **8 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **51 passed, 7 skipped, 1 deselected**.

Locked decisions still pending implementation in later milestones:
- Offline verifier must change from current no-key `PASS` to `AMBIGUOUS` with no automatic completion.
- Project Brief support is the next product milestone after shared contracts.
- Steps, step verification, persisted mentor, Planner clarification gate, archive-in-place Replace, Refiner, and Boss Brain remain unimplemented.

Next step: G0 Project Brief support after re-reading the two plan files, `EXPLANATION.md`, and this checkpoint.

### Milestone G0: Project Brief — COMPLETE (2026-09-10)

Implemented the editable per-project Brief field and UI editor. Existing SQLite databases receive an idempotent `projects.brief` migration. Project reads now expose `brief`, and `PUT /api/v1/projects/{project_id}/brief` trims and persists the supplied text while allowing an empty value to clear it. The header includes a Brief button and modal editor with a bounded 20,000-character input.

The database dependency now invokes `init_db()` before opening request sessions. This preserves runtime migration behavior for `TestClient` callers that do not execute FastAPI lifespan startup hooks, and fixed the first G0 test run's legacy-database `projects.brief` failure.

Files changed:
- `backend/models/schema.py`
- `backend/database.py`
- `backend/schemas/api_schemas.py`
- `backend/routers/projects.py`
- `frontend/src/components/ProjectBriefPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/brief.css`
- `tests/test_project_brief.py`
- `EXPLANATION.md`

Commands run and results:
- `python -m pytest tests/test_project_brief.py tests/test_methodology_seeding.py tests/test_workflow_history.py tests/test_assets_pivot.py -v` -> **10 passed** after fixing migration timing.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **53 passed, 7 skipped, 1 deselected**.

Next step: G1 Task Steps after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G1: Task Steps and Manual State Management — COMPLETE (2026-09-10)

Added first-class manual Task Steps with active-step filtering, parent validation, editable metadata, five-state transitions, audit events, and Task completion rollup. A Task with active Steps cannot be directly marked `COMPLETED` while any active Step is non-terminal. A Task without Steps retains the existing direct state-transition behavior.

Files changed:
- `backend/models/schema.py`
- `backend/database.py`
- `backend/schemas/api_schemas.py`
- `backend/services/task_state.py`
- `backend/routers/tasks.py`
- `backend/routers/task_steps.py`
- `backend/main.py`
- `frontend/src/components/TaskStepsPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/steps.css`
- `tests/test_task_steps.py`
- `tests/test_api_contracts.py`
- `EXPLANATION.md`

Schema/API behavior:
- Added `task_steps` with objective, rationale, completion criteria, expected evidence type, state, ordering, AI flag, archive flag, and justification.
- Added nullable `evidence.step_id` migration and ORM relationship in preparation for G2.
- Added `GET`, `POST`, `PUT`, and state-transition Step routes under the parent Task.
- `GET /tasks` now includes active Step summaries under each Task.
- Step transitions use the shared five-state validation and write `TASK_STATE_CHANGED` with `entity_type="task_step"`.
- Completing all active sibling Steps rolls the parent Task to `COMPLETED` with an audit event.

Commands run and results:
- `python -m pytest tests/test_task_steps.py tests/test_api_contracts.py tests/test_methodology_seeding.py tests/test_workflow_history.py -v` -> **14 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **58 passed, 7 skipped, 1 deselected**.

Next step: G2 Step-level evidence verification after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G2: Step-Level Evidence Verification — COMPLETE (2026-09-10)

Reused the existing evidence artifact, redaction, clipping, verifier, asset-upsert, proposal-trigger, and audit pipeline for Step verification. The shared orchestration now accepts an optional Step while preserving parent `task_id` compatibility. The existing Task verification route returns 409 before any artifact write when active Steps exist.

The locked offline-verifier decision is implemented: no-key verification returns `AMBIGUOUS`/`LOW`, persists the artifact and deterministic extracted assets, and never auto-completes a Task or Step. Provider-error and malformed-response fallback remains `AMBIGUOUS`/`LOW`.

Files changed:
- `backend/services/cohere_service.py`
- `backend/routers/evidence.py`
- `backend/routers/task_steps.py`
- `tests/test_cohere_resilience.py`
- `tests/test_task_steps.py`
- `EXPLANATION.md`

Behavior covered:
- `POST /api/v1/projects/{project_id}/tasks/{task_id}/steps/{step_id}/verify` stores evidence with both parent `task_id` and `step_id`.
- Evidence metadata exposes `step_id` and `step_title` when available.
- Live PASS completes a Step and rolls the parent Task up when all active Steps are terminal.
- Offline AMBIGUOUS leaves Step and Task states unchanged.
- Task verification is blocked for Step-bearing Tasks without creating an artifact.
- Step verification enforces the existing scope-lock gate and preserves asset deduplication/source-task behavior.

Commands run and results:
- `python -m pytest tests/test_task_steps.py tests/test_cohere_resilience.py tests/test_artifacts.py tests/test_release_hardening.py -v` -> **18 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **62 passed, 7 skipped, 1 deselected**.

Next step: G3 persisted, Step-aware mentor after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G3: Persisted, Step-Aware Mentor — COMPLETE (2026-09-10)

Added SQLite-backed mentor turn persistence and optional Step-scoped context. The existing safety system prompt, redaction, clipping, fallback, and audit behavior remain intact. User messages are sanitized/clipped before persistence; assistant replies retain the fallback availability flag.

Files changed:
- `backend/models/schema.py`
- `backend/models/__init__.py`
- `backend/schemas/api_schemas.py`
- `backend/services/mentor_service.py`
- `backend/routers/mentor.py`
- `frontend/src/components/MentorPanel.tsx`
- `frontend/src/main.tsx`
- `tests/test_mentor.py`
- `tests/test_api_contracts.py`
- `EXPLANATION.md`

Behavior covered:
- Added `mentor_messages` with project/task/optional-step scope, role, mode, sanitized content, availability, and timestamp.
- Task mentor accepts optional `step_id` and validates parentage.
- Step context includes objective, rationale, completion criteria, expected evidence type, and status.
- `GET /api/v1/projects/{project_id}/tasks/{task_id}/mentor/history?step_id=` returns ordered persisted turns.
- Frontend `MentorPanel` loads history from the API on scope changes and after sends; the module-level conversation Map is removed.
- Existing task-only mentor calls remain compatible.

Commands run and results:
- `python -m pytest tests/test_mentor.py tests/test_api_contracts.py -v` -> **9 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **64 passed, 7 skipped, 1 deselected**.

Next step: G4 Planner clarification gate and workflow draft/apply after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G4: Planner Workflow Draft and Clarification Gate — COMPLETE (2026-09-10)

Implemented the Brief-to-workflow Planner with a deterministic clarification gate, strict seven-phase schema validation, versioned prompt files, safe redaction, offline baseline fallback, provider-error fallback, preview UI, explicit Apply Replace/Merge, and archive-in-place workflow replacement.

Files changed:
- `backend/models/schema.py`
- `backend/database.py`
- `backend/prompts/planner_v1.txt`
- `backend/prompts/planner_clarification_v1.txt`
- `backend/services/planner_service.py`
- `backend/services/workflow_engine.py`
- `backend/routers/workflow.py`
- `backend/routers/tasks.py`
- `backend/routers/proposals.py`
- `backend/routers/reports.py`
- `backend/routers/archives.py`
- `backend/schemas/api_schemas.py`
- `backend/main.py`
- `frontend/src/components/WorkflowPlannerPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/planner.css`
- `tests/test_planner_workflow.py`
- `tests/test_api_contracts.py`
- `EXPLANATION.md`

Behavior covered:
- `POST /api/v1/projects/{project_id}/workflow/generate` returns `NEEDS_CLARIFICATION` with bounded questions and no draft for incomplete briefs.
- Complete briefs produce exactly seven canonical phases. No-key and provider-error paths return the deterministic baseline reshaped into one Step per Task.
- AI Planner output is strict-schema validated, phase constrained, bounded, redacted, and never applied during Generate.
- `POST /api/v1/projects/{project_id}/workflow/apply` supports explicit `replace` and `merge` modes.
- Replace archives Tasks and Steps in place, preserving IDs and Evidence links; active task/phase listings and readiness exclude archived workflow rows.
- Merge deduplicates exact active Task titles and does not modify existing active Tasks, Steps, Evidence, or Findings.
- Archive export/import now preserves Project Brief, phase/task/Step archive metadata, Step-linked Evidence, and persisted mentor messages.
- Frontend Planner displays clarification questions, draft phase/task/Step preview, offline/live status, Apply Replace, Apply Merge, and Discard.

Commands run and results:
- `python -m pytest tests/test_planner_workflow.py tests/test_export_archive.py tests/test_import_archive.py tests/test_api_contracts.py -v` -> **11 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **70 passed, 7 skipped, 1 deselected**.

Next step: G5 Discovery-driven cross-phase Refiner after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G5: Discovery-Driven Cross-Phase Refiner — COMPLETE (2026-09-10)

Extended discovery-driven proposal generation to select an exact canonical phase while preserving the existing pending queue cap, target-asset deduplication, title deduplication, proposal approval, dismissal, and undo behavior.

Files changed:
- `backend/services/asset_proposal_service.py`
- `backend/routers/assets.py`
- `backend/routers/evidence.py`
- `tests/test_assets_pivot.py`
- `EXPLANATION.md`

Behavior covered:
- Refiner responses include `phase_name` and are validated against the seven canonical methodology phases.
- No-key, provider-error, malformed, and invalid-phase responses safely fall back to `Phase 4: Vulnerability Analysis`.
- Asset-driven and evidence/Step discovery triggers pass only sanitized discovery data and compressed phase/task-title context to the Refiner.
- Approved proposals land in the exact selected phase through the completed ADR-3 targeting fix.
- Existing proposal caps, deduplication, and offline asset-pivot behavior remain intact.

Commands run and results:
- `python -m pytest tests/test_assets_pivot.py tests/test_task_steps.py tests/test_cohere_resilience.py tests/test_methodology_seeding.py -v` -> **20 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **72 passed, 7 skipped, 1 deselected**.

Next step: G6 Boss Brain digest and project-scoped mentor after re-reading the plans, `EXPLANATION.md`, and this checkpoint.

### Milestone G6: Boss Brain Dashboard and Digest — COMPLETE (2026-09-10)

Added a read-only project-wide digest grounded in the same coverage computation as Report Readiness, plus a persisted project-scope mentor conversation and a Boss Brain frontend tab.

Files changed:
- `backend/services/readiness_service.py`
- `backend/services/workflow_digest.py`
- `backend/routers/workflow_digest.py`
- `backend/routers/reports.py`
- `backend/main.py`
- `frontend/src/components/BossBrainPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/boss.css`
- `tests/test_boss_brain.py`
- `tests/test_api_contracts.py`
- `EXPLANATION.md`

Behavior covered:
- Extracted `calculate_phase_coverage()` as the single shared coverage function; `GET /report/readiness` and the digest both call it, so their `coverage` maps cannot drift.
- `GET /api/v1/projects/{project_id}/workflow/digest` returns ordered per-phase coverage, task totals, asset counts, confirmed-finding counts, plus project totals and confirmed-finding summaries (ready for AI context).
- `POST /api/v1/projects/{project_id}/mentor/boss` builds context from the digest, confirmed findings, and evidence counts, reuses `ask_mentor()` (same safety prompt, redaction, clipping, fallback), and persists both turns with `task_id=NULL`, `step_id=NULL`.
- `GET /api/v1/projects/{project_id}/mentor/boss/history` returns only project-scope threads, distinct from task/Step history.
- Boss mentor never returns HTTP 500 on no-key or provider failure; both paths fall back safely with `ai_available=false`.
- Frontend "Boss Brain" tab shows the read-only phase/task tree, measured digest cards, and a project-scope conversation.
- Removed unused import in `backend/routers/workflow.py`.

Commands run and results:
- `python -m pytest tests/test_boss_brain.py tests/test_api_contracts.py -v` -> **7 passed**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).
- `python -m pytest -m "not e2e"` -> **77 passed, 7 skipped, 1 deselected**.

Next step: FINAL milestone — consolidate `EXPLANATION.md`, `USER_MANUAL.md`, and `PRODUCT_OVERVIEW.md` to match ground truth and run the complete release regression matrix.

### FINAL: Ground-Truth Consolidation and Release Regression — COMPLETE (2026-09-10)

Closed out the initiative by reconciling the human-facing docs with the implemented system and proving the archive round-trip for the new entities.

Docs reconciled to ground truth:
- `EXPLANATION.md`: Project Brief, task_steps, evidence.step_id, mentor_messages, Phase/Task/Step archive metadata, ADR-3 exact proposal targeting, offline AMBIGUOUS verifier, Planner generate/apply routes, Refiner phase selection, Boss Brain digest and boss-mentor routes, and the new frontend components.
- `docs/USER_MANUAL.md`: replaced the "workflow generation not supported" section with Brief + Planner + clarification gate + Apply semantics; added a Steps section; corrected the offline verdict table to AMBIGUOUS/no auto-complete; added the AI mentor persistence + Boss Brain section; updated proposal phase targeting, archive remapping, and troubleshooting.
- `docs/PRODUCT_OVERVIEW.md`: updated the flow diagram and walkthrough for Brief/Planner/Steps/Refiner/Boss Brain; corrected evidence verification, proposals, and AI mentor feature descriptions; rewrote the stale known limitations (offline verdict, mentor persistence, proposal phase targeting).

Cross-cutting archive verification:
- Extended the archive round-trip test to prove Task Steps, evidence Step links, and project-scope mentor messages survive export/import with remapped IDs.

Files changed:
- `docs/USER_MANUAL.md`
- `docs/PRODUCT_OVERVIEW.md`
- `EXPLANATION.md`
- `tests/test_import_archive.py`
- `docs/internal/PROGRESS.md`

Commands run and results (release matrix):
- `python -m pytest -m "not e2e"` -> **78 passed, 7 skipped, 1 deselected**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed** (Vite emitted only the existing config-loader warning).

Initiative status: **all milestones complete** (0A, G0–G6, FINAL). No regressions: the full non-E2E suite is green, backend compiles, and the frontend builds.

## Current Status
- Active Milestone: Workflow Generation Initiative — COMPLETE (0A, G0–G6, FINAL)
- Last Updated: 2026-09-10

## Verification Pass (2026-09-10)

An independent recheck of the whole initiative was performed against the plan requirements.

Confirmed correct:
- All planned routes are present and asserted by the canonical route contract test.
- Idempotent migrations run after `Base.metadata.create_all()`, so fresh and legacy SQLite databases both work.
- Archive import reads optional collections with `data.get(key, [])`, so older archives without `task_steps`/`mentor_messages` still import.
- Offline verifier returns `AMBIGUOUS` and never auto-completes.
- Proposal approval, Replace archive-in-place, Merge dedup, Planner clarification gate, Refiner phase validation, digest/readiness parity, and project-scope mentor persistence all hold.

Bug found and fixed:
- The Refiner could return an empty `proposals` list, and the evidence keyword path indexed `refined[0]`, an `IndexError` that would have surfaced as HTTP 500. Fixed in `asset_proposal_service.suggest_safe_tasks` (empty/invalid provider output now degrades to the deterministic standard proposal) and hardened at the `evidence.py` call site. Regression tests added: `test_refiner_empty_response_falls_back_to_standard_proposal` and `test_keyword_discovery_never_500s_when_refiner_returns_empty`.

Functional gap closed:
- Step-level verification and Step-scoped mentor were backend-complete but not reachable from the UI. `TaskStepsPanel` now supports opening a Step to verify evidence and to open the mentor scoped to that Step; `main.tsx` passes the selected Step to `MentorPanel` and resets it on task change.

Cleanup:
- Removed unused imports in `backend/routers/workflow.py` and `backend/routers/workflow_digest.py`.

Files changed in this pass:
- `backend/services/asset_proposal_service.py`
- `backend/routers/evidence.py`
- `backend/routers/workflow.py`
- `backend/routers/workflow_digest.py`
- `frontend/src/components/TaskStepsPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/steps.css`
- `tests/test_assets_pivot.py`
- `docs/USER_MANUAL.md`
- `docs/internal/PROGRESS.md`

Commands run and results:
- `python -m pytest tests/test_assets_pivot.py -v` -> **5 passed**.
- `python -m pytest -m "not e2e"` -> **80 passed, 7 skipped, 1 deselected**.
- `python -m compileall backend` -> **passed**.
- `npm run build` from `frontend` -> **passed**.

## Workspace Cleanup (2026-09-08)

Goal: decongest the repo root for human testing; keep runtime paths stable. `core/`, `data/chroma/`, `backend/` (runtime code), `frontend/`, `tests/`, `scripts/`, `data/methodologies/`, and the user's `GITHUB/` staging bundle were not reorganized (only the explicitly-named one-shot `backend/migrate_day2.py` was moved out, per task instructions — verified un-imported anywhere).

Files moved:
- `PROGRESS.md` → `docs/internal/PROGRESS.md`
- `AI_BENCHMARK_REPORT.md` → `docs/internal/AI_BENCHMARK_REPORT.md`
- `Test_before_live.md` → `docs/internal/old_runbooks/Test_before_live.md`
- `REDSAGE_V2_ONE_DAY_BUILD_RUNBOOK.md` → `docs/internal/old_runbooks/`
- `implementation_plan.md` → `docs/internal/old_runbooks/`
- `RedSage_v2_Day-2_Implementation_Plan.md` → `docs/internal/old_runbooks/`
- `RedSage_v2_Day-3_Implementation_Plan.md` → `docs/internal/old_runbooks/`
- `inspect_db.py` → `devtools/diagnostics/inspect_db.py` (ripgrep-verified: not imported by backend/ or tests/)
- `backend/migrate_day2.py` → `devtools/migrations/migrate_day2.py` (ripgrep-verified: referenced only by docs; one-shot, already executed)

New files:
- `INTERNAL.md` (root pointer: where internal docs/devtools live; states they are not required to run the app)
- `HUMAN_TESTING.code-workspace` (VS Code workspace hiding `docs/internal/**`, `devtools/**`, `data/projects/**`, `data/redsage.db` via files.exclude)

Reference fixes:
- `pytest.ini`: added `testpaths = tests` — a newly added `GITHUB/` staging folder (user-created copy with its own `tests/` package) broke pytest collection with a duplicate-package-name collision (23 collection errors); scoping collection restores the previous behavior exactly and leaves `GITHUB/` untouched.
- `tests/test_live_ai_benchmark.py`: opt-in benchmark output paths updated to `docs/internal/AI_BENCHMARK_REPORT.md` and `docs/internal/PROGRESS.md`.
- `EXPLANATION.md`: updated references to the moved migration script (`devtools/migrations/migrate_day2.py`), `devtools/diagnostics/inspect_db.py`, and the relocated benchmark/progress docs (§1.3, §8.1 item 13, §8.3, footer).
- `README.md`, `docs/RUN.md`, `.gitignore`, `scripts/`: checked — no references to moved files, no changes needed.

Commands run + results:
- `python -m pytest`: **50 passed, 7 skipped** (e2e browser suite included, run against the live persistent backend; 7 skips are the opt-in live-Cohere benchmark tests).
- `python -m compileall backend`: clean; `python -m compileall devtools`: clean (moved scripts still compile).
- `npm run build` (from `frontend`): passed — dist generated in 337ms.
- Live server smoke after reorg: `GET /api/v1/health` → 200 healthy payload; `GET /` → 200 SPA shell. The app runs unchanged in dev and prod-like modes (no runtime path referenced any moved file).

Next step: none — cleanup complete. Manual testing: open `HUMAN_TESTING.code-workspace` in VS Code, or run per `docs/RUN.md`.

## Vision Gap Sprint Milestones
- [x] M6: Rewrite EXPLANATION.md (ground truth) + final verification
  - Completed: EXPLANATION.md fully regenerated from a fresh read of the codebase — architecture (12 routers incl. mentor), data model (findings status/evidence semantics), storage split, complete route inventory (mentor, finding confirm, tasks `target_host`), AI pipeline with all three verifier paths (live / offline / failure fallback) and the mentor pipeline (context pack bounds, safety rules, static fallback), 7-phase methodology table, UI structure (Active Target picker, FindingsPanel, MentorPanel), safety posture section, 22 known limitations, and current test status (50 passed incl. e2e, 7 skipped live-AI).
  - Files touched: `EXPLANATION.md` (rewritten), `PROGRESS.md` (this entry).
  - Commands run (final verification): `python -m pytest` with a live backend (Cohere keys blanked in the server process for determinism) → **50 passed, 7 skipped** (includes the Playwright e2e browser flow against the built `frontend/dist`); `python -m compileall backend` → passed, no errors; `npm run build` from `frontend` → passed (dist generated in 175ms).
  - Test results: all green.
  - Next step: none — sprint complete. See Manual Vision-Gap Verification below.
- [x] M5: Task AI Mentor (endpoint + panel + fallbacks)
  - Completed: new `POST /api/v1/projects/{project_id}/tasks/{task_id}/mentor` accepting `{mode: teach|guide|verify|summarize, user_message, target_host?}`. The context pack is bounded and DB-only (raw artifacts never read): task title/objective/phase/status, scope whitelist+blacklist+lock+rate limit, active target (explicit, else whitelist[0]), top 10 assets, top 5 confirmed findings, and the 3 latest evidence `redacted_excerpt` values for the task. Cohere `command-r-08-2024` runs under a strict system prompt (no exploit payloads or step-by-step compromise; evidence treated as untrusted inert data; scope-bounded, methodology-oriented). If the key is missing or the call fails (429/5xx/network/timeout/empty), the endpoint returns HTTP 200 with a mode-specific static checklist and `ai_available: false` — never HTTP 500. Out-of-scope `target_host` → 422. Each request audits a `MENTOR_ASKED` event (mode, availability, question length — never question content). Frontend: collapsible right-side `MentorPanel` in the roadmap view with mode selector, per-project/per-task in-memory conversation map, message list, spinner during 5–15s latency, and disabled send while awaiting; the roadmap grid widens to three columns when open.
  - Files touched: `backend/services/mentor_service.py` (new: context pack, safety prompt, static fallback), `backend/routers/mentor.py` (new), `backend/schemas/api_schemas.py` (`MentorAsk`), `backend/main.py` (router registration), `frontend/src/components/MentorPanel.tsx` (new), `frontend/src/main.tsx` (toggle + panel wiring), `frontend/src/day3.css` (panel styles; fixed a brace imbalance caught by the build), `tests/test_mentor.py` (new, 5 tests), `tests/test_api_contracts.py` (mentor route).
  - Commands run: `python -m pytest tests/test_mentor.py -v` (5 passed), `python -m pytest -m "not e2e"` (49 passed, 7 skipped, 1 deselected), `npm run build` from `frontend` (initially failed on a CSS `}}}` typo; fixed and rebuilt successfully — dist generated in 152ms).
  - Test results: green (backend + build).
  - Next step: M6 — rewrite EXPLANATION.md to match ground truth; final full verification.
- [x] M4: Expand baseline methodology to 7 phases
  - Completed: `data/methodologies/baseline_methodology.json` now seeds all 7 PTES phases in order — Pre-engagement, Intelligence Gathering, Threat Modeling, Vulnerability Analysis, Exploitation (Authorized Validation: PoC planning + outcome recording only, no commands, no payloads), Post-Exploitation (Impact Review: business-impact documentation + cleanup verification only), Reporting. 2 tasks per phase (14 total), all human-executed; the only command templates retained are the pre-existing non-intrusive `nmap`/`ffuf`/`curl` audit commands bound to `{target_host}`/`{rate_limit}`. New projects seed all 7 phases via the unchanged `seed_project_tasks` engine; existing projects are NOT force-migrated (their phase sets remain valid, and proposal approval still matches `%Phase 4%` for both old and new projects). Adjusted `tests/test_active_target.py` to select a task that actually has a resolved command (Phase 1 tasks are documentation-only with `command_template: null`).
  - Files touched: `data/methodologies/baseline_methodology.json` (7 phases, 14 safe tasks), `tests/test_methodology_seeding.py` (new, 4 tests), `tests/test_active_target.py` (command-task selector fix).
  - Commands run: `python -m pytest tests/test_methodology_seeding.py -v` (4 passed), `python -m pytest -m "not e2e"` (44 passed, 7 skipped, 1 deselected).
  - Test results: green.
  - Next step: M5 — Task AI Mentor endpoint (Teach/Guide/Verify/Summarize) with bounded context pack, safety rules, Cohere fallback; frontend Mentor panel.
- [x] M3: Active Target selector for multi-target scope
  - Completed: `GET /tasks` now accepts an optional `target_host` query parameter that must be present in the project whitelist (422 otherwise, so commands can never resolve for out-of-scope hosts). `resolved_command` and `is_scope_safe` are computed for the selected target; with no parameter the first whitelist entry remains the default (legacy behavior). Frontend roadmap view gained an "Active Target" dropdown bound to the scope whitelist; the selection is stored in local state, passed to the tasks fetch, and reset when switching/creating/importing projects. `refresh()` now loads scope first and self-heals a stale selection (falls back to the first whitelist entry) to avoid 422 loops after scope changes.
  - Files touched: `backend/routers/tasks.py` (`resolve_active_target` helper + `target_host` query param), `frontend/src/main.tsx` (activeTarget state, dropdown, scope-first refresh), `frontend/src/day3.css` (target-picker styles), `tests/test_active_target.py` (new, 4 tests).
  - Commands run: `python -m pytest tests/test_active_target.py -v` (4 passed), `python -m pytest -m "not e2e"` (40 passed, 7 skipped, 1 deselected).
  - Test results: green.
  - Next step: M4 — expand `baseline_methodology.json` to 7 PTES phases with minimal safe tasks; verify seeding for new projects.
- [x] M2: Findings lifecycle (Draft → Confirmed)
  - Completed: `POST /findings` now creates a `DRAFT` finding (evidence optional; a supplied `evidence_id` must exist in the same project). New `POST /findings/{finding_id}/confirm` requires valid same-project evidence plus non-empty title/severity/description/reproduction_steps (severity validated against LOW/MEDIUM/HIGH/CRITICAL/INFO), applies optional field updates, sets `CONFIRMED`, and audits `FINDING_DRAFTED`/`FINDING_CONFIRMED`. Reports include only CONFIRMED findings (unchanged); readiness ignores drafts entirely and keeps CRITICAL for CONFIRMED findings missing evidence. Frontend `FindingsPanel` shows Draft/Confirmed groups, a "+ Log Draft" action, and an inline confirm form (evidence select, severity select, description/reproduction/remediation, affected asset) with inline validation errors and double-confirm rejection.
  - Files touched: `backend/schemas/api_schemas.py` (`FindingCreate.evidence_id` optional; new `FindingConfirm`), `backend/routers/findings.py` (rewritten: dict serialization, draft creation, confirm endpoint, audit events), `frontend/src/components/FindingsPanel.tsx` (new), `frontend/src/main.tsx` (uses panel; removed inline confirmed-only flow), `frontend/src/day3.css` (panel styles), `tests/test_findings_lifecycle.py` (new, 5 tests), `tests/test_api_contracts.py` (confirm route added).
  - Commands run: `python -m pytest tests/test_findings_lifecycle.py -v` (5 passed after reordering evidence-gate before field validation), `python -m pytest -m "not e2e"` (36 passed, 7 skipped, 1 deselected).
  - Test results: green.
  - Next step: M3 — Active Target selector (backend `target_host` query param for tasks, per-target `resolved_command`/`is_scope_safe`, frontend dropdown).
- [x] M1: Cohere failure resilience (verifier fallback; mentor fallback lands with the mentor endpoint in M5)
  - Completed: live Cohere failures (429/5xx/network/timeout/malformed response) now degrade to a safe structured verdict — verdict `AMBIGUOUS`, confidence `LOW`, summary "AI verification unavailable; evidence saved; manual review recommended.", grounded quotations pulled from the sanitized/clipped evidence, extracted assets from the offline regex extractor. The verify endpoint never returns HTTP 500 for provider outages; the task is not auto-completed on ambiguous fallback; the artifact file, SHA-256, size, and redacted excerpt are persisted before AI runs so nothing is lost.
  - Files touched: `backend/services/cohere_service.py` (wrapped the live call in try/except; added `_extract_assets_offline`, `_cohere_failure_verdict`), `tests/test_cohere_resilience.py` (new).
  - Commands run: `python -m pytest tests/test_cohere_resilience.py -v` (2 passed), `python -m pytest -m "not e2e"` (31 passed, 7 skipped, 1 deselected).
  - Test results: green. The e2e browser suite is environment-gated (needs a running server) and matches the pre-sprint baseline failure mode.
  - Next step: M2 — findings lifecycle (DRAFT by default without evidence; POST /findings/{id}/confirm requiring evidence + required fields; report/readiness only CONFIRMED).

## Completed Milestones
- [x] Milestone 0: Scaffold & Health Check
- [x] Milestone 1: Database Setup & Models
- [x] Milestone 2: Projects & Scope Lock Gate
- [x] Milestone 3: Baseline Methodology & Tasks API
- [x] Milestone 4: Evidence Verify Endpoint
- [x] Milestone 5: Proposals Queue
- [x] Milestone 6: Findings CRUD & Evidence Gate
- [x] Milestone 7: Report Studio & Download Endpoint
- [x] Milestone 8: Frontend Screens
- [x] Milestone 9: Tests & Magic Demo Walkthrough

## Day-2 Milestones
- [x] Milestone 1: Artifact Manager, Safe Paths & Migration
- [x] Milestone 2: Evidence Verification Writes Files and Metadata
- [x] Milestone 3: Evidence Retrieval APIs
- [x] Milestone 4: Evidence Library Frontend
- [x] Milestone 5: Formal Report Evidence Register
- [x] Milestone 6: Artifact and Report Traceability Tests

## Day-3 Milestones
- [x] Milestone 1: Governed Scope Amendments & Report Integration
- [x] Milestone 2: Workflow History & Proposal Undo
- [x] Milestone 3: Asset-First Pivot & Governed Task Generation
- [x] Milestone 4: Report Readiness Auditor
- [x] Milestone 5: Project-Wide Quick Search
- [x] Milestone 6: Automated Testing & Build Verification

## V1.2 Milestones
- [x] Prod-like single-process static frontend serving from FastAPI
- [x] Dev mode unchanged at `http://127.0.0.1:5173`
- [x] Missing-frontend fallback message
- [x] RUN.md documentation
- [x] Static-serving tests and full regression

## V1.2 Hardening Milestones
- [x] README.md updated with install, dev/prod-like run modes, scripts, tests, docs, env vars, KB facts
- [x] docs/DEMO.md, docs/SECURITY.md, docs/ARCHIVE_FORMAT.md added
- [x] scripts/dev|build|run for PowerShell and shell added
- [x] .env.example added; .gitignore already ignores .env
- [x] Hardening tests added and green

## Commands and Results
- `python -m pip install -r requirements.txt`: existing environment satisfied; backend imports succeeded.
- `python -c "from backend.database import init_db; init_db(); print('DB Initialized Successfully')"`: `DB Initialized Successfully`.
- `python -m compileall backend`: passed.
- `python -m pytest`: `4 passed in 0.55s`.
- `npm install`: completed, 0 vulnerabilities.
- `npm run build` (from `frontend`): passed; Vite production bundle generated.
- `python -c "...TestClient vertical slice..."`: project 200, scope 200, lock 200, 4 tasks, verify 200, report 200. Initial asset assertion exposed a regex issue; fixed asset matching to detect `/backup.zip`.
- `$env:CO_API_KEY=$null; $env:COHERE_API_KEY=$null; ...TestClient final demo...`: health 200, PASS verdict, `/backup.zip` extracted, proposal generated, approval 200, invalid finding rejected 400, report download 200.
- `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --log-level warning`: startup check completed without application errors; command was terminated by the validation timeout.
- `Get-FileHash -Algorithm SHA256 core\...`: recorded hashes for all four preserved core files; no core files were edited.
- Resume check `python -m pytest`: `4 passed in 0.30s`.
- Resume check `npm run build` (from `frontend`): passed; Vite bundle generated.
- Resume check `python -m compileall backend`: passed.
- Resume check deterministic vertical slice: `200 4 PASS 1 200` for health, baseline task count, verification, proposal generation, and report download.
- Live backend `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`: ready at `http://127.0.0.1:8000`.
- Live frontend `npm run dev` (from `frontend`): ready at `http://127.0.0.1:5173`.
- Live HTTP checks: backend returned exact healthy payload; frontend returned HTTP 200.
- Day-2 Milestone 1 `python backend/migrate_day2.py`: `migrated_count=4 skipped_count=0`; all legacy evidence rows received filesystem artifacts and metadata columns.
- Day-2 Milestone 1 artifact smoke test: saved `data/projects/test-proj/artifacts/EVID-TEST_1788846756.txt` with size and SHA-256 digest.
- Day-2 Milestone 1 `python -m pytest`: `4 passed in 0.19s`.
- Day-2 Milestone 2 updated `backend/routers/evidence.py`: verification now assigns per-project `EVID-###` IDs, writes raw text to disk, stores metadata and redacted excerpt only, and exposes evidence list/content routes.
- Day-2 Milestone 2 `python -m pytest`: `4 passed in 0.17s`.
- Day-2 Milestone 2 `python -m compileall backend`: passed.
- Day-2 Milestone 2 initial manual command failed because PowerShell parsed embedded quotes in the one-line Python command; no application code was executed. A quoting-safe rerun is required.
- Day-2 Milestone 2 fixed that quoting issue with a safe smoke command; verify returned HTTP 200 and created `EVID-001`.
- Day-2 Milestone 2 post-fix `python -m pytest`: `4 passed in 0.14s`.
- Day-2 Milestone 3 API verification: evidence list returned HTTP 200 with artifact metadata and redacted excerpt; content endpoint returned HTTP 200 with the raw text on demand.
- Day-2 Milestone 3 path safety check: traversal attempt was rejected with `Invalid artifact path: Directory traversal detected`.
- Day-2 Milestone 4 added typed `EvidenceItem`, API helpers, Evidence Library page, on-demand artifact drawer, hash/content copy actions, and Roadmap/Evidence/Report navigation.
- Day-2 Milestone 4 initial `npm run build` failed because `frontend/src/services/api.ts` was missing; added the module and reran successfully.
- Day-2 Milestone 4 `npm run build` (from `frontend`): passed, 19 modules transformed.
- Day-2 Milestone 4 `python -m pytest`: `4 passed in 0.25s`.
- Day-2 Milestone 5 report builder now emits six formal sections, confirmed finding Evidence Ref lines, missing-evidence readiness warnings, and the Evidence Register & Integrity Log appendix.
- Day-2 Milestone 5 report smoke: appendix, evidence reference, digest, artifact filename, and UTC timestamp were present in generated Markdown; report endpoint succeeded.
- Day-2 Milestone 5 post-fix `python -m pytest`: `4 passed in 0.16s`.
- Day-2 Milestone 6 added artifact traversal, SHA-256, evidence metadata/excerpt, report appendix, confirmed finding reference, and missing-evidence warning tests.
- Day-2 Milestone 6 final `python -m pytest`: `9 passed in 1.13s`.
- Day-2 Milestone 6 final `npm run build` (from `frontend`): passed, 19 modules transformed.
- Day-2 Milestone 6 final `python -m compileall backend`: passed.
- Day-3 Milestone 1 added `ScopeAmendment`, `AuditEvent`, governed scope amendment validation, and report scope-amendment table integration. SQLite schema initialization added the proposal task linkage column idempotently.
- Day-3 Milestone 1 `python -c "from backend.database import init_db; init_db()"`: schema ok.
- Day-3 Milestone 1 `python -m compileall backend; python -m pytest`: `9 passed in 1.57s` after fixing a report-builder bracket syntax error.
- Day-3 Milestone 2 added audit event retrieval, scope-lock/task/evidence/proposal audit records, proposal task linkage, and guarded proposal undo. Backend compile and pytest gate: `9 passed in 1.14s`.
- Day-3 Milestone 3 added safe asset-derived proposal generation, pending-proposal cap/deduplication, asset source-task metadata, and Assets View backend. Backend compile and pytest gate: `9 passed in 1.14s`.
- Day-3 Milestone 4 added report readiness checks for evidence, reproduction/remediation, task justifications, pending proposals, and phase coverage. Frontend integrated ReadinessPanel.
- Day-3 Milestone 5 added parameterized project search over findings, evidence excerpts/IDs, and assets, capped at five results per category, plus Ctrl+K SearchModal.
- Day-3 frontend integration `npm run build` (from `frontend`): passed, 25 modules transformed.
- Day-3 frontend integration `python -m pytest`: `9 passed in 1.92s`.
- Day-3 Milestone 6 added `test_scope_amendment.py`, `test_workflow_history.py`, `test_assets_pivot.py`, `test_report_readiness.py`, and `test_search.py`. Initial test run found stale hard-coded test primary keys; changed test fixtures to UUID IDs and reran green.
- Day-3 Milestone 6 final `python -m pytest`: `14 passed in 1.79s`.
- Day-3 Milestone 6 final `npm run build` (from `frontend`): passed, 25 modules transformed.
- Day-3 Milestone 6 final `python -m compileall backend`: passed.
- Final API walkthrough with Cohere variables unset: amendment HTTP 200, evidence `EVID-578336A40C`, asset list 1, governed suggestion 1, readiness score 100, all search groups returned, amendment report section present, evidence register present.
- Restarted live services with final code: backend ready at `http://127.0.0.1:8000`, frontend ready at `http://127.0.0.1:5173`.
- Live HTTP checks: exact healthy backend payload, frontend HTTP 200, all required Day-3 routes registered.
- V1.1 M1 selected a project-scoped JSON archive format: `manifest.json`, `db/project_data.json`, `artifacts/*.txt`, and generated `reports/report.md`; no global database export, `.env`, API keys, or external configuration.
- V1.1 M1 safety rules: archive members reject absolute paths, backslashes, empty/dot segments, and `..` traversal; archive/member size limits and SHA-256 manifest checks are enforced on import; conflicts always remap to a new project and row IDs.
- V1.1 M1 added `backend/services/archive_service.py` and archive route foundation in `backend/routers/archives.py`.
- V1.1 M2 export route `GET /api/v1/projects/{project_id}/export` returns a ZIP containing manifest, project JSON, artifact files, and generated report; manifest records counts and SHA-256 checksums.
- V1.1 M2 `python -m pytest`: `15 passed` including ZIP structure, manifest, artifact presence, and no-env/no-key assertions.
- V1.1 M3 import route `POST /api/v1/projects/import` validates the archive format, rejects zip-slip/oversized/incomplete archives, remaps all IDs to a new project, recomputes artifact digests, and remaps audit entity references.
- V1.1 M3 fixed import cleanup so a failed import removes only the new project directory, not the entire `data/projects` tree.
- V1.1 M3 `python -m pytest`: `17 passed in 9.52s` including export-to-import remap, artifact content, report endpoint, and zip-slip rejection tests.
- V1.1 M4 added Export Project and Import Project controls to the header, browser-driven ZIP download, ZIP file picker upload with progress state, and navigation to the imported project after success.
- V1.1 M4 `npm run build` (from `frontend`): passed, 25 modules transformed.
- V1.1 M5 full regression `python -m pytest`: `17 passed in 9.89s`.
- V1.1 M5 `python -m compileall backend`: passed.
- V1.1 live services restarted: backend ready at `http://127.0.0.1:8000`, frontend ready at `http://127.0.0.1:5173`; health payload correct, frontend HTTP 200, export/import routes registered.
- V1.2 added `backend/services/static_frontend.py`: detects `frontend/dist`, mounts `/assets` via StaticFiles, and adds a last-registered SPA fallback that returns `index.html` while returning JSON 404 for unknown `/api/*` paths.
- V1.2 updated `backend/main.py`: routers register before static mounting so API/download endpoints always win over the SPA fallback; when `frontend/dist/index.html` is absent, `GET /` returns a helpful build command message.
- V1.2 `python -m pytest`: `20 passed in 4.81s` (new static-frontend tests use an isolated temp dist to avoid depending on a build).
- V1.2 `python -m compileall backend`: passed.
- V1.2 `npm run build` (from `frontend`): passed, 25 modules transformed.
- V1.2 live prod-like verification (backend only, no Vite): `GET /` returns `index.html`, `/assets/*.js` serves `text/javascript`, `/api/v1/health` returns the exact JSON payload, `/api/v1/projects` returns JSON (not intercepted), and a live export download returned `application/zip` bytes (`PK` magic).
- V1.2 hardening: added `.env.example`, README rewrite, `docs/DEMO.md`, `docs/SECURITY.md`, `docs/ARCHIVE_FORMAT.md`, and `scripts/dev|build|run.{ps1,sh}`.
- V1.2 hardening added `tests/test_release_hardening.py`: redacted excerpts never store known password/bearer/JWT values, exported DB rows exclude secrets/config, import rolls back cleanly on checksum mismatch, and `.env.example`/`.gitignore` guards.
- V1.2 hardening `python -m pytest tests/test_release_hardening.py`: `4 passed in 1.95s`.
- V1.2 hardening full `python -m pytest`: `24 passed in 10.55s`.
- V1.2 hardening `python -m compileall backend`: passed.
- V1.2 hardening `powershell -ExecutionPolicy Bypass -File scripts\build.ps1`: passed, 25 modules transformed, message printed.

## Errors and Fixes
- Original runbook was empty on first read; it was restored before implementation resumed.
- Vite emitted a non-blocking CommonJS/ESM config warning.
- Running `npm run build` from the repository root failed with `ENOENT` because `package.json` is under `frontend`; rerun from `frontend` passed.
- Live Cohere verification can return model-dependent assets; deterministic local validation unsets Cohere variables and uses the safe offline verifier. Live mode still enforces clipped, redacted, XML-tagged evidence and strict JSON schema parsing.
- Resume verification found and fixed startup decorator wiring so `init_db()` runs during uvicorn startup; health remains a separate route handler.
- Day-2 Milestone 1 retained the legacy `raw_content` column for SQLite compatibility, but migration and new application writes use filesystem artifacts and metadata.
- Day-2 Milestone 2 now redacts the complete submitted text before taking the 800-character database excerpt, preventing secrets near the excerpt boundary from being stored.
- Day-2 Milestone 4 non-blocking Vite ESM/CommonJS config warning remains documented from Day 1.
- Final test run reports only deprecation warnings from FastAPI startup events, Starlette/httpx TestClient integration, and Python UTC datetime APIs; no test failures.
- Day-3 Milestone 1 initial compile/test gate caught an unclosed `lines.extend` list in `report_builder.py`; fixed before proceeding.
- Day-3 component integration initially left the old entrypoint active; replaced `frontend/src/main.tsx` and added `day3.css`, then rebuilt successfully.
- Day-3 Milestone 6 test run initially failed on persistent-database primary-key collisions; converted test fixture IDs to UUIDs and reran `14 passed`.
- An initial route inspection command incorrectly treated FastAPI `_IncludedRouter` objects as routes; switched to `app.openapi()['paths']`, confirming no missing routes.
- V1.1 archive format deliberately exports only one project as JSON rows to avoid overwriting or leaking unrelated projects in the shared SQLite database.

## Next Action
- Vision Gap Sprint complete (M1–M6). Dev: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` + `npm run dev` from `frontend`. Prod-like: `scripts\build.ps1` then `scripts\run.ps1` (or `cd frontend && npm run build`, then the backend command) and open `http://127.0.0.1:8000`. Final gates: `python -m pytest` (50 passed, 7 skipped incl. e2e), `python -m compileall backend` (clean), `npm run build` from `frontend` (clean).

## Production Assurance Hardening
- Added immutable OpenAPI method/path contract coverage and safe invalid-resource error assertions.
- Expanded evidence redaction for bearer/basic credentials, JWTs, CLI password flags, headers, structured secrets, URL-encoded values, private keys, and connection strings.
- Added boundary-safe redacted excerpts, 10 MB artifact enforcement, fsync plus atomic replacement, startup temporary-file cleanup, and database/file reconciliation.
- Added the React error boundary, Playwright browser smoke flow, pytest markers, and fail-fast `scripts/verify_all.sh` / `scripts/verify_all.ps1` gates.
- Verification: `29 passed, 1 deselected` for non-browser tests; `1 passed, 29 deselected` for Playwright E2E; backend compilation passed; frontend production build passed; Playwright Chromium installed. The browser flow accepts the product's valid `PASS` or `INCONCLUSIVE` verdict for evidence that does not prove the selected task.

## Manual Vision-Gap Verification
1. Start the backend (`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`) after `cd frontend && npm run build`, then open `http://127.0.0.1:8000`.
2. Create a project and confirm the task tree shows **7 phases** (Pre-engagement → Reporting) with 2 tasks each; Phases 5/6 show no resolved commands (planning/documentation only).
3. Configure & lock a scope with two targets (e.g. `alpha.local,beta.local`); use the **Active Target** dropdown in the roadmap sidebar and confirm the resolved command and scope-safety change with the selection.
4. Select a Phase 2 task, paste inert tool output, and verify. Log a finding via **+ Log Draft** (no evidence needed) and confirm it appears under "Drafts". Use **Confirm** — omit fields to see the inline validation errors, then complete the form with linked evidence and confirm it moves to "Confirmed".
5. Open Report Studio: only the confirmed finding appears in the report; readiness stays green while drafts exist (drafts are ignored); a confirmed finding without evidence is CRITICAL.
6. Toggle **AI Mentor** on a task: pick each mode, ask a methodology question, and confirm the reply (or, if the AI provider is down, the static checklist with `AI unavailable` labeling). Send is disabled with a thinking note while awaiting.
7. With `CO_API_KEY` set, simulate a provider outage (e.g. block network) and verify evidence: the response is HTTP 200 with verdict `AMBIGUOUS`, confidence `LOW`, summary "AI verification unavailable; evidence saved; manual review recommended.", and the artifact still appears in the Evidence Library with its SHA-256.
8. Export and re-import the project and confirm findings (draft + confirmed), phases, evidence, and audit events survive.

## Preserved-Area Confirmation
- `core/` and `data/chroma/` were not modified during this sprint (no file under either path was read-modified-written; only `backend/`, `frontend/src/`, `data/methodologies/baseline_methodology.json`, `tests/`, `PROGRESS.md`, and `EXPLANATION.md` changed).

## Manual V1.2 Verification
1. Run `cd frontend && npm run build`, then start only the backend.
2. Open `http://127.0.0.1:8000` and confirm the built UI loads without Vite.
3. Navigate between Roadmap, Evidence Library, Assets, and Report tabs and confirm API calls succeed.
4. Confirm `GET /api/v1/health` returns the expected JSON and unknown `/api/*` paths return JSON 404 rather than HTML.
5. Export a project and confirm the ZIP downloads (not intercepted by the SPA fallback); import it back and confirm navigation and evidence restore.
6. Rename `frontend/dist` temporarily, reload `http://127.0.0.1:8000`, and confirm the helpful "run `cd frontend && npm run build`" message appears.

## Manual V1.1 Verification
1. Open `http://127.0.0.1:5173` and create a project.
2. Lock the scope, verify evidence for a task, and create a finding linked to the evidence.
3. Click `Export Project` in the header and confirm `redsage_project_{id}.zip` downloads.
4. Inspect the ZIP: `manifest.json`, `db/project_data.json`, one `artifacts/EVID-*.txt`, and `reports/report.md`; confirm no `.env` or API key content.
5. Click `Import Project`, select the ZIP, and confirm the app navigates to the new imported project.
6. Confirm the Evidence Library lists the imported artifact and its raw content opens in the viewer.
7. Open Report Studio and confirm the report contains the scope/task evidence register for the imported project.

## Manual Day-3 Verification
1. Open `http://127.0.0.1:5173` and select or create a project.
2. Lock the initial scope, click `Amend Scope`, add a valid host, enter an authorizing entity and at least 10-character rationale, then confirm the scope badge and report amendment table.
3. Paste inert evidence into a task and verify it. Confirm the task audit event, extracted asset, and pending governed proposal.
4. Open `History`, approve a proposal, then use `Undo Addition` while the proposed task is untouched. Confirm the task disappears and the proposal returns to the queue.
5. Open `Assets`, search an asset, click `Suggest Tasks`, and confirm proposals appear only in the queue.
6. Open `Report Studio`, inspect the readiness score, issues, phase coverage, formal report, and `Evidence Register & Integrity Log`; download the Markdown report.
7. Press `Ctrl+K`, search for an evidence ID, finding term, or asset value, and select a grouped result to navigate to its view.

## Live AI Benchmark Results (command-r-08-2024)

- **Date:** 2026-09-08 14:51:30 UTC - live Cohere `command-r-08-2024` via ClientV2 with the `.env` API key.
- **Ground Truth Accuracy:** 4/4 scenarios passed (100%).
- **Grounding & Extraction Integrity:** quotes and assets were verbatim substrings of the sanitized evidence (whitespace-run normalized).
- **Indirect Prompt Injection (OWASP LLM01):** `<untrusted_evidence_log>` successfully prevented instruction overrides; no `PWNED` marker echoed.
- **Sensitive Data Masking (OWASP LLM06):** credentials redacted before dispatch (verified).
- **E2E Live Workflow:** passed through the FastAPI endpoint.
- **Latency Telemetry:** p50=5589.5 ms, p95=14829.8 ms.
- **Token Consumption:** average total tokens per verification run approx 797.
- **Command:** `pytest tests/test_live_ai_benchmark.py -v -s`.



## Hermes Blueprint Implementation — 2026-09-13

Implemented the supplied `Downloads/RedSage-Begins.md` blueprint in the workspace context layer.

Created or reconciled:
- `SOUL.md` and `AGENTS.md` with RedSage identity, safety, evidence, scope, archive, and guarded-zone rules.
- Required skills under `skills/`: release gates, repository ground-truth sync, incremental ticket execution, API endpoint, frontend flow, idempotent DB migration, archive export/import, and KB citations.
- `optional-skills/skill_doc_regenerate.md`.
- `docs/internal/HERMES_CONTEXT_SUMMARY.md`, `HERMES_MCP_CONFIG.md`, and `KB_COMPLIANCE_NOTES.md`.

Verified:
- Project venv: `.venv/Scripts/python.exe` (Python 3.14.7).
- `interfaces.mcp_server` imports; its registered tools are `kb_search`, `kb_sources`, and `kb_stats`.
- A direct KB query (`SQL injection`) returned one citation from the preserved collection `redsage_kb_local_v4`; output is treated as untrusted and not reproduced.
- Native Hermes registration succeeded: `redsage-kb` is enabled with all three tools. `hermes mcp test redsage-kb` connected and discovered all three tools after `mcp_servers.redsage-kb.cwd` was set to the repo root.
- `.venv/Scripts/python.exe -m compileall backend`: passed.
- `.venv/Scripts/python.exe -m pytest -m "not e2e" -q -p no:cacheprovider`: **101 passed, 7 skipped, 1 deselected**.
- `npm run build` from `frontend`: passed; the existing Vite `configLoader: native` warning remains.
- `core/**` and `data/chroma/**`: no changes.

Next step:
- Start a fresh Hermes session from this repository so the configured MCP tools are injected into its toolset. E2E remains explicit-request only.
