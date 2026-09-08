# EXPLANATION.md — RedSage v2 Ground Truth

This document is the source of truth for what this public release is, how it
works, what is deliberately included and excluded, and how the pieces fit
together. Read this before modifying or redistributing the project.

## 1. What RedSage is

RedSage v2 is a **local-first, single-operator, human-in-the-loop security
assessment workflow companion**. It is a documentation, governance, and
reporting tool for authorized penetration-testing and audit engagements.

The core design decision: **RedSage never touches the target**. It does not
execute security tooling, launch scans, open sockets, run the commands it
displays, or automate attacks. The human operator performs all testing outside
the application using their own tooling, then pastes the resulting output into
RedSage as evidence. RedSage's job is to keep that evidence governed and
traceable:

- enforce and audit the engagement scope,
- guide the operator through a standard methodology,
- redact and safely store evidence,
- optionally verify evidence against task objectives,
- track findings that are linked to evidence,
- compile audit-ready reports, and
- export/import projects without losing integrity.

## 2. Workflow

1. **Project** — the operator creates a project.
2. **Scope lock** — the operator configures `in_scope_whitelist`,
   `out_of_scope_blacklist`, and `max_rate_limit`, then locks the scope.
   Evidence verification and in-scope command resolution are disabled until
   the lock is set. Scope amendments require a valid target, an authorizing
   entity, and a rationale; every amendment is written to `scope_amendments`
   and `audit_events`.
3. **Methodology** — each new project is seeded with 7 PTES phases
   (Pre-engagement, Intelligence Gathering, Threat Modeling, Vulnerability
   Analysis, Exploitation (Authorized Validation), Post-Exploitation (Impact
   Review), Reporting) from `data/methodologies/baseline_methodology.json`.
   Exploitation and post-exploitation phases contain planning/documentation
   tasks only — no command templates.
4. **Task & evidence** — the operator picks a task, performs the step
   manually, and pastes tool output into the Evidence tray. RedSage clips the
   log, regex-redacts secrets in memory, stores the full artifact on disk
   under `data/projects/{project_id}/artifacts/`, and stores only a redacted
   excerpt plus metadata (SHA-256 digest) in the database.
5. **Verification** — if `CO_API_KEY` (or `COHERE_API_KEY`) is set, Cohere
   reviews the sanitized evidence against the task objective and returns a
   structured JSON verdict (`PASS`/`FAIL`/`AMBIGUOUS`/`CONFIRMED_NEGATIVE`
   with grounded quotations). If no key is set, a deterministic local verifier
   runs; if Cohere fails, a safe `AMBIGUOUS` fallback verdict is returned.
   Provider failures never block evidence persistence.
6. **Assets & proposals** — extracted hosts/ports/endpoints/files become
   assets; exposed-asset findings can generate governed proposals that require
   explicit approval before they create new tasks.
7. **Findings** — findings carry severity, description, reproduction steps,
   and a linked evidence ID. Confirmation requires a valid evidence link.
8. **Report** — Report Studio checks readiness (scope locked, evidence linked,
   no unresolved blockers) and renders a Markdown report with an evidence
   register appendix and integrity log.
9. **Export/import** — export produces a ZIP with `manifest.json` (checksums),
   `db/project_data.json`, artifacts, and an optional report snapshot. Import
   validates format, paths (zip-slip/absolute-path rejection), size caps, and
   SHA-256 checksums before writing; imported projects receive new IDs with
   foreign keys remapped and never overwrite existing projects.

## 3. Architecture

```
frontend/ (React + Vite)  ──HTTP──▶  backend/ (FastAPI)
                                        │  routers: projects, scope, tasks, evidence,
                                        │           proposals, findings, reports, audit,
                                        │           assets, search, archives, mentor
                                        │  services: workflow_engine, scope_validator,
                                        │           artifact_manager, cohere_service,
                                        │           report_builder, archive_service,
                                        │           recovery_service, audit_service,
                                        │           asset_proposal_service, mentor_service,
                                        │           static_frontend
                                        ▼
                              SQLite (data/redsage.db, created at runtime)
                              Evidence artifacts (data/projects/, created at runtime)
```

- The backend is a single FastAPI process; in prod-like mode it also serves
  the built React app from `frontend/dist`.
- Persistence is SQLAlchemy over a local SQLite file; `init_db()` creates
  tables on startup and applies two idempotent migrations for
  `workflow_proposals.created_task_id` and `assets.source_task_id`.
- Startup also runs `reconcile_storage_and_db()`: it removes stale temp
  artifact files and logs evidence rows that reference missing artifacts.
- There is **no authentication and no multi-user model**; the threat model is
  a single operator on a trusted local machine. Bind to `127.0.0.1`.

## 4. Data boundaries and redaction

- The database stores metadata and **redacted excerpts only** — never raw
  evidence. Raw evidence lives on disk as artifacts.
- Redaction patterns (in `backend/services/cohere_service.py`) cover bearer
  tokens, basic-auth headers, JWTs, `password=`/`--password` assignments,
  `-H authorization:` headers, `secret`/`api_key`/`token`/`private_key`
  assignments, PEM private-key blocks, and URI-embedded credentials in common
  connection strings. URL-encoded values are decoded before redaction.
- Evidence logs are clipped to a bounded number of lines before processing,
  and AI prompts wrap sanitized evidence in `<untrusted_evidence_log>`
  boundaries, instructing the model to treat the content as inert data and to
  return JSON matching a strict schema.
- Offline mode: with no Cohere key configured, **no data leaves the machine**.

## 5. What is in this release

| Path | Purpose |
|---|---|
| `backend/` | FastAPI engine (routers, services, models, schemas) |
| `frontend/` | React + Vite UI source |
| `tests/` | pytest suite (unit, integration, and Playwright e2e) |
| `scripts/` | dev/build/run/verify helpers (PowerShell + shell) |
| `data/methodologies/baseline_methodology.json` | Safe, authorization-focused PTES methodology seed |
| `docs/` | RUN, SECURITY, DEMO, ARCHIVE_FORMAT |
| `EXPLANATION.md`, `README.md`, `LICENSE`, `.env.example`, `.gitignore` | Ground truth, onboarding, MIT license, configuration template |
| `.github/workflows/ci.yml` | CI: backend tests + frontend build |

## 6. What is deliberately NOT in this release

| Excluded | Reason |
|---|---|
| `data/redsage.db` | Local runtime database — created fresh on first run |
| `data/projects/` | Real engagement evidence artifacts — sensitive, never public |
| `data/chroma/` and `core/` | Preserved KB vectors and engine — proprietary/organizational data |
| `.env` | Real API keys and local configuration — never committed |
| `frontend/node_modules/`, `frontend/dist/` | Build artifacts — reproduce with `npm install` / `npm run build` |
| Planning docs, runbooks, benchmark reports | Internal process documents, not user-facing release material |

The application **does not depend on any of the excluded paths to run**: the
backend never imports the KB engine, and startup creates the database and
project directories on demand. `frontend/dist` is optional (the root route
shows a build hint when it is missing).

## 7. Safety posture

- Commands shown by the app are **suggestions for the human operator**, gated
  on locked scope and in-scope targets; the app never executes them.
- The methodology seed avoids exploit/payload tooling entirely; the
  exploitation phase is planning/validation documentation only.
- All testing must be covered by explicit written authorization matching the
  locked project scope. The tool's scope controls are workflow guards, not
  substitutes for legal authorization or network-level controls.
- Run only on trusted machines, bound to loopback, and keep a backup of
  `data/redsage.db` and `data/projects/` if you need to preserve engagement
  records.

## 8. Verification of this release

Before publishing, run:

```powershell
python scripts/verify_public_bundle.py   # fails on secrets/forbidden files
python -m pytest -m "not e2e"            # unit + integration tests
cd frontend; npm ci; npm run build; cd .. # frontend build check
```

See `docs/RUN.md` and `docs/SECURITY.md` for operational detail.
