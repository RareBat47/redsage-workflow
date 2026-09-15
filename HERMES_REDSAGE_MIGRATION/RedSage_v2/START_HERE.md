# START HERE

**Read this first.** It is the onboarding entry point for any new AI agent or developer picking up RedSage v2.

---

## 1. What This Project Is

RedSage v2 is a **local-first, single-operator, human-in-the-loop penetration-testing and audit workflow companion**. The operator performs every action manually outside the application and **pastes the raw output back in as evidence** — RedSage never executes tools, scans, opens sockets to targets, or automates attacks. It provides the governed workflow around that work: authorization scope management, a Project Brief and AI workflow Planner, a seven-phase methodology, guided Task Steps, evidence verification with integrity hashing, governed cross-phase proposals, a findings lifecycle, audit-ready reports, and portable project archives.

---

## 2. Ground Truth Rule

> **EXPLANATION.md is the authoritative technical reference. If any other document disagrees with EXPLANATION.md or with the actual code, the code wins, then EXPLANATION.md, in that order. Always verify claims against the real code before acting on any documentation, including this file.**

Corollary: `docs/internal/` (including `PROGRESS.md`), the archive folder `docs/internal/completed_initiatives/`, and any historical plan are **records of past intent, not descriptions of current behavior**.

---

## 3. Non-Negotiable Safety Rules

Copied verbatim from `EXPLANATION.md` §9.1 (Safety Posture):

1. **No execution.** No route runs a command, opens a socket, or shells out. `command_template`/`resolved_command` are inert strings substituted for display only.
2. **No exploit content.** The Planner schema rejects `command_template` containing `exploit`, `payload`, `reverse shell`, or `meterpreter`; the Refiner always nulls `command_template`; the mentor and verifier system prompts forbid exploit material and step-by-step compromise instructions; baseline Phases 5–6 carry no commands.
3. **Human-in-the-loop.** AI output is always a proposal or a draft. Applying a workflow requires an explicit `POST /workflow/apply`; approving a proposal is a human action; completion happens through an explicit state transition or a validated live `PASS`.
4. **Evidence before conclusions.** Findings cannot be confirmed without project-scoped evidence; verification is refused while scope is unlocked.
5. **No silent data loss.** Artifacts are written atomically and hashed; provider failures are downgraded, not raised; workflow Replace archives in place instead of deleting; archive import is transactional with rollback and directory cleanup.

Additional operational rule: **every AI surface must have a deterministic no-key path and a failure path, and must never return HTTP 500 on provider failure.** The offline evidence verifier returns `AMBIGUOUS` and never auto-completes work.

---

## 4. What's Already Built

Summary from the regenerated `EXPLANATION.md`:

- **Projects & scope** — create/list/get projects with an editable **Project Brief**; whitelist/blacklist scope with lock and audited amendments; scope lock gates evidence verification; non-whitelisted targets rejected.
- **Seven-phase methodology** — seeded from `data/methodologies/baseline_methodology.json` (7 phases × 2 tasks = 14 tasks); display-only command templates in Phases 2 and 4 only.
- **Evidence pipeline** — paste-only capture; atomic hashed artifact storage (SHA-256, 10 MB cap); redaction (10 pattern families, URL-decode aware) and 80-line clipping before any provider call; verdicts `PASS` / `FAIL` / `AMBIGUOUS` / `CONFIRMED_NEGATIVE`; grounded quotations and asset extraction.
- **AI workflow Planner** — Brief → deterministic clarification gate → seven-phase draft → preview → **Apply Replace (archives in place) / Apply Merge (exact-title dedup) / Discard**; offline and provider-failure fallback to the baseline reshape; canonical phase list has a single source of truth.
- **Task Steps** — `task_steps` with objective, why-it-matters, completion criteria, expected evidence type; five-state machine shared with tasks; **Step→Task completion rollup**; Step-level evidence verification with a 409 guard that disables task-level verification when active Steps exist.
- **Mentor with 4 modes** — `teach`, `guide`, `verify`, `summarize`; scoped to task, Step, or project (Boss Brain); context bounded at 8,000 chars from DB metadata only (raw artifacts never read); **conversations persisted** in `mentor_messages` and reload across restarts; static-checklist fallback without a key.
- **Cross-phase proposals with AI-driven phase selection** — keyword-triggered and asset-suggestion proposals; the Refiner chooses a canonical `phase_name` (invalid/absent → Phase 4 fallback); approval targets the **exact** stored phase; pending cap of 5; dismiss and constrained undo.
- **Boss Brain dashboard** — read-only per-phase digest (coverage, assets, confirmed findings) computed by the **same coverage helper as Report Readiness**, plus a persisted project-scope AI conversation.
- **Findings lifecycle** — DRAFT → CONFIRMED, confirmation gated on project-scoped evidence; audit events for drafting and confirming.
- **Reporting** — Markdown report with scope attestation, methodology matrix, asset inventory, confirmed findings, and an Evidence Register appendix (file name, size, SHA-256, timestamp); readiness score and issue list.
- **Export/import archives** — checksummed ZIP (format v1.0) with zip-slip and expansion defenses, full ID remapping, transaction rollback, and mentor-message coverage.

---

## 5. How to Run This Project

### Install (once)

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd frontend
npm install
cd ..
```

Python 3.11+ recommended; Node 18+.

### Dev mode (two terminals)

```powershell
# Terminal 1 — backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

- UI: `http://127.0.0.1:5173` · API: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs`

### Prod-like local mode (single process)

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` — FastAPI serves both the built UI and the API. Convenience scripts: `scripts\dev.ps1`, `scripts\build.ps1`, `scripts\run.ps1` (Shell equivalents alongside).

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/redsage.db` | Workflow SQLite database |
| `CO_API_KEY` / `COHERE_API_KEY` | unset | Enables live AI (planner, verifier, mentor, refiner). **Unset = fully offline deterministic mode** |
| `REDSAGE_CHROMA_DIR` / `REDSAGE_DB` / `REDSAGE_COLLECTION` | see README | Auxiliary preserved KB engine (`core/`) |

Binding defaults to `127.0.0.1`. **Do not expose this service to untrusted networks — there is no authentication on any endpoint.**

---

## 6. How to Run Tests

```powershell
python -m pytest -m "not e2e"
```

**Expected baseline (regenerated audit, 2026-09-11): 83 passed, 7 skipped, 0 failed, 1 deselected** (91 collected / 90 selected).

- **7 skipped** = `tests/test_live_ai_benchmark.py`, opt-in live-provider tests. They need a real `CO_API_KEY`; run them explicitly with `python -m pytest tests/test_live_ai_benchmark.py -v -s`.
- **1 deselected** = `tests/e2e/test_browser_suite.py`, marked `e2e` in `pytest.ini`; it needs a running server plus Playwright Chromium. Running plain `python -m pytest` collects it.
- Supporting gates: `python -m compileall backend` and `cd frontend && npm run build`.
- **Hygiene warning:** the suite uses the configured database and writes real rows/artifacts into `data/redsage.db` and `data/projects/`. Repeated runs accumulate data — use a dedicated `DATABASE_URL` if you want isolation.

---

## 7. Where to Look Before Changing Anything

| Area | Location |
|---|---|
| Data model (12 tables) | `backend/models/schema.py` |
| API routes (15 routers) | `backend/routers/` → `projects`, `scope`, `tasks`, `task_steps`, `evidence`, `proposals`, `findings`, `reports`, `audit`, `assets`, `search`, `archives`, `mentor`, `workflow`, `workflow_digest` |
| App wiring / router registration / migrations | `backend/main.py`, `backend/database.py` |
| AI verification (redaction, clipping, verdicts) | `backend/services/cohere_service.py` |
| AI guidance (4 modes, context pack, persistence write) | `backend/services/mentor_service.py`, `backend/routers/mentor.py` |
| AI workflow generation (clarification gate, drafts) | `backend/services/planner_service.py`, `backend/routers/workflow.py`, `backend/prompts/planner_v1.txt` |
| AI proposals / phase selection (Refiner) | `backend/services/asset_proposal_service.py` |
| Boss Brain digest | `backend/services/workflow_digest.py`, `backend/services/readiness_service.py` |
| Step state machine & rollup | `backend/services/task_state.py` |
| Artifacts, archives, reports | `backend/services/artifact_manager.py`, `archive_service.py`, `report_builder.py`, `backend/routers/archives.py` |
| Frontend entry | `frontend/src/main.tsx` (single `App`, `View` union, no router) |
| Frontend API client | `frontend/src/services/api.ts` (hardcoded `127.0.0.1:8000/api/v1`) |
| Schema validation contracts | `backend/schemas/api_schemas.py` |
| Full route/behavior reference | `EXPLANATION.md` |

**Do not modify:** `core/`, `data/chroma/` (preserved knowledge base and vectors).

---

## 8. Known Open Issues

Full lists: `EXPLANATION.md` §8.3 (documentation/implementation discrepancies) and `PROJECT_AUDIT_SUMMARY.md` §5 and §7 (findings and risk register). Top five by priority:

1. **Report matrix inconsistency (Medium).** `GET /report` and `/report/download` include archived tasks in the methodology matrix (`reports.py:11`), while the report snapshot embedded in an export excludes them (`archives.py:86`). The same project can produce two different reports — needs a product decision.
2. **Finding evidence re-pointing (Low–Medium).** `POST /findings/{id}/confirm` overwrites the stored `evidence_id` with the payload value instead of validating equality (`findings.py:69`), so a confirmation can silently change a draft's evidence link.
3. **No authentication anywhere (High if exposed).** Single-operator, loopback-only by design. `.env` may hold a live provider key: gitignored and excluded from archives, but it travels with folder copies. Rotate before distribution and never bind to a routable interface.
4. **Unpinned frontend dependencies (Medium for reproducibility).** `frontend/package.json` declares every dependency as `"latest"` with no committed lockfile.
5. **Per-request migrations (Low, performance).** `get_db()` calls `init_db()` on every request, running `create_all()` plus seven reflection/DDL blocks each time (`database.py:12-20`). Correct but wasteful.

Also noted: the non-E2E suite pollutes the dev database (see §6), and `planner_service` makes `cohere` a hard import-time dependency even offline.

---

## 9. How Planning Works Here

Feature work in this project follows a **two-document pattern**: a **Product Plan** (what/why, behavior-level, no code) and an **Implementation Plan** (milestone-gated, file-level, with explicit Definition-of-Done and "do not touch" boundaries per milestone).

See `docs/internal/completed_initiatives/workflow_generation_2026/` for a worked example of this pattern before starting new feature planning. That archive contains the completed Product Plan, Implementation Plan, workspace inventory, and full project details for the workflow-generation initiative.

Milestone-by-milestone build history and test logs are in `docs/internal/PROGRESS.md`.

---

## 10. Current Project Data State

As of 2026-09-11, the default database at `data/redsage.db` contains:

| Metric | Value |
|---|---|
| Projects | **1,343** |
| Evidence records | 500 |
| Artifact project directories (`data/projects/`) | 478 |
| Database size | ~27.1 MB |

**This is almost entirely development and test clutter** — the automated test suite writes real rows into the configured database on every run. Before starting fresh feature work, decide whether to reset `data/redsage.db` and `data/projects/` (and whether to preserve `data/chroma/`, which is preserved knowledge-base data and must **not** be deleted). Data lifecycle decisions belong to the user; no agent should reset or delete this data unilaterally.
