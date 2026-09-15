# RedSage v2 — User Manual

This manual walks through installation, both run modes, and every operator workflow in the current build. It reflects the behavior implemented on disk (`backend/**`, `frontend/src/**`), not plans or assumptions. RedSage never executes tools: every command you see is display-only text, all testing is performed manually outside the application, and all evidence is pasted in by you under explicit written authorization.

---

## 1. Installation and prerequisites

**Required**

- **Python 3.10 or newer** (the verification script asserts 3.10+; the project is verified against 3.14 with chromadb 1.5.9).
- **Node.js 18+** with `npm` (for building or running the frontend).
- Git is not required; run from the repository root (`RedSage_v2/`).

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd frontend
npm install
cd ..
```

**macOS / Linux**

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend
npm install
cd ..
```

**Optional configuration**

Copy `.env.example` to `.env` if you want to change defaults:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/redsage.db` | Workflow SQLite database |
| `CO_API_KEY` / `COHERE_API_KEY` | unset | Enables live Cohere verification, suggestions, and mentor |
| `APP_ENV`, `DEBUG` | development / true | Local settings |
| `REDSAGE_CHROMA_DIR`, `REDSAGE_DB`, `REDSAGE_COLLECTION`, `REDSAGE_EMBEDDING_PROVIDER`, `REDSAGE_TOP_K`, `REDSAGE_SCORE_THRESHOLD` | see `.env.example` | Preserved knowledge-base engine only (not used by the workflow UI) |

Without an API key the application runs fully offline: verification uses a deterministic local verifier and nothing leaves your machine. Never commit a real key.

**Data locations created at runtime**

- `data/redsage.db` — workflow database (metadata and redacted excerpts only).
- `data/projects/{project_id}/artifacts/` — full raw evidence files.
- `frontend/dist/` — built UI, created by `npm run build`.

`core/` and `data/chroma/` are preserved legacy components and are not modified by the workflow application.

---

## 2. Run modes

### 2.1 Dev mode (two terminals)

Frontend dev server with hot reload plus the backend API.

**Terminal 1 — backend**

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

- API root: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/api/v1/health`
- Interactive API docs (Swagger): `http://127.0.0.1:8000/docs`

**Terminal 2 — frontend**

```powershell
cd frontend
npm run dev
```

- UI: `http://127.0.0.1:5173`

The backend enables CORS for exactly `http://127.0.0.1:5173` and `http://localhost:5173`. The React app always calls `http://127.0.0.1:8000/api/v1` directly, so the backend must stay on port 8000 (see Troubleshooting #1).

### 2.2 Single-command mode (backend serves `frontend/dist`)

Build the UI once, then run only the backend; FastAPI serves the SPA and the API from the same origin.

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. API routes are registered before the SPA fallback, so `/api/v1/*`, report downloads, and export/import continue to work. If `frontend/dist/index.html` is missing, `GET /` returns a dark-themed page telling you to run `cd frontend && npm run build`.

### 2.3 Convenience scripts

| Task | PowerShell | Shell |
|---|---|---|
| Dev mode (backend + Vite, separate windows) | `scripts\dev.ps1` | `scripts/dev.sh` |
| Frontend production build | `scripts\build.ps1` | `scripts/build.sh` |
| Single-process prod-like run | `scripts\run.ps1` | `scripts/run.sh` |
| Full verification (compile, pytest, build, e2e) | `scripts\verify_all.ps1` | `scripts/verify_all.sh` |

`scripts\run.ps1` exits with an error if `frontend/dist/index.html` does not exist; run the build script first.

---

## 3. First-run checklist

1. Start the backend and open `http://127.0.0.1:8000/api/v1/health` — you should see `status: healthy` and `human_in_the_loop: true`.
2. Open the UI (5173 in dev mode, or 8000 in single-command mode). With no project selected you see the welcome panel: **"Authorized testing, documented."**
3. Click **+ New Project** and create an engagement. The Roadmap Canvas should show seven phases with 14 seeded tasks (see §5).
4. Click **Configure & Lock Scope**, enter an authorized target, and confirm the header badge changes to **SCOPE LOCKED**.
5. Select a Phase 2 task and confirm the resolved command shows your target (Active Target selector, §7.2).
6. Paste an inert sample log and click **Verify Evidence**; confirm the verdict card and the **Saved as EVID-…** line appear.
7. Open the **Evidence Library** tab and check the artifact's size, SHA-256, and redacted excerpt.
8. If the evidence named a keyword-bearing asset, check the **Proposals** queue in the left panel.
9. Log a draft finding, confirm it with linked evidence, and open **Report Studio** to check the readiness score.
10. Click **History** to see the audit trail (`SCOPE_LOCKED`, `TASK_STATE_CHANGED`, `EVIDENCE_VERIFIED`, …).
11. Click **Export Project** and confirm the ZIP downloads.

At every startup the backend also runs a reconciliation pass: stale temp files in artifact folders are deleted and any evidence row whose file is missing on disk is logged as `CRITICAL "Evidence … references missing artifact"`. This result is a server-side log only; it is not shown over HTTP.

---

## 4. Creating a project

1. Click **+ New Project** in the header.
2. Enter a project name in the prompt (1–200 characters) and confirm. The default suggestion is `OWASP Juice Shop Audit`.
3. The new project is added to the project selector, becomes active, and the Roadmap Canvas loads.

Behind the scenes:

- `POST /api/v1/projects` creates the project (`target_type` defaults to `web_app`; description is optional via the API but not asked in the UI).
- An empty scope row is created (whitelist `[]`, blacklist `[]`, rate limit 10, unlocked).
- The baseline methodology is seeded immediately (§5).
- Use the project dropdown in the header to switch engagements; switching resets the Active Target to the first whitelist entry (or empty).

---

## 5. Project Brief and workflow generation

The Project Brief and AI Planner are supported in this build.

**Project Brief** — click **Brief** in the header to open the editor. The brief is free text (up to 20,000 characters) describing the engagement type, authorized scope, constraints, timebox, and desired assessment focus. It is stored per project and can be cleared by saving empty text.

**Planner** — click **Planner** in the header to open the Workflow Planner:

1. **Generate Workflow** calls `POST /api/v1/projects/{id}/workflow/generate`.
2. If the brief is materially incomplete, the Planner returns **NEEDS_CLARIFICATION** with bounded questions and **no draft**. Answer the questions, choose **Save Answers and Generate**, and the answers are appended to the brief before regenerating. This gate is a prerequisite, not a chat.
3. When the brief is complete, the Planner returns a draft that always contains exactly the seven canonical phases. With a Cohere key the draft is tailored to the brief; with no key or on provider error the deterministic baseline is reshaped into the same schema (one Step per baseline Task).
4. **Preview** the draft, then choose **Apply Replace (Archive Old)**, **Apply Merge**, or **Discard Draft**. Nothing touches the live roadmap until an Apply action.
   - **Replace** archives the existing active Tasks and Steps in place (preserving their IDs and Evidence links) and inserts the new workflow.
   - **Merge** adds only Tasks whose titles do not already exist verbatim among active Tasks in that phase.

If the brief is empty or missing engagement details, generation is blocked until the questions are answered.

### Baseline methodology (offline fallback and new-project seed)

New projects are still seeded automatically at creation by `seed_project_tasks()` from `data/methodologies/baseline_methodology.json` (**7 phases × 2 tasks = 14 tasks**):

| # | Phase | Tasks | Commands |
|---|---|---|---|
| 1 | Phase 1: Pre-engagement | 1.1 Confirm Authorization & Rules of Engagement; 1.2 Validate Scope Coverage & Testing Windows | none (documentation) |
| 2 | Phase 2: Intelligence Gathering | 2.1 Active Port & Service Discovery; 2.2 Web Content & Directory Discovery | `nmap …`, `ffuf …` templates with `{target_host}` / `{rate_limit}` |
| 3 | Phase 3: Threat Modeling | 3.1 Map Assets & Trust Boundaries; 3.2 Prioritize the Attack Surface | none |
| 4 | Phase 4: Vulnerability Analysis | 4.1 Transport Security & HTTP Header Audit; 4.2 Authentication Surface Analysis | `curl` audit templates |
| 5 | Phase 5: Exploitation (Authorized Validation) | 5.1 Plan Authorized Proof-of-Concept Validation; 5.2 Record Validation Outcome & Evidence Capture | **none — planning/recording only, no payloads** |
| 6 | Phase 6: Post-Exploitation (Impact Review) | 6.1 Document Business Impact of Validated Findings; 6.2 Verify No Persistence & Clean Up Test Artifacts | **none — documentation only** |
| 7 | Phase 7: Reporting | 7.1 Draft Findings With Evidence References; 7.2 Review Readiness & Deliver the Report | none |

Notes:

- Existing projects are **not** migrated when the methodology changes; only newly created projects receive the full 7-phase set. Older projects keep their original phases.
- Proposal approval targets the phase whose name exactly matches the proposal's `phase_name`, so cross-phase proposals land where the Refiner intended.
- Commands are inert templates rendered for a human. RedSage never runs them.

---

## 5A. Steps (substeps)

Each task can be expanded into **Steps** through the **Task Steps** panel on the Roadmap. Steps let you break a task into checkpoints with their own objective, rationale, completion criteria, and expected evidence type.

- **Add Step** creates a manual Step (title required). Steps are ordered and can be edited (`PUT …/steps/{step_id}`).
- Steps use the same five statuses as tasks (NOT_STARTED, IN_PROGRESS, COMPLETED, SKIPPED, CONFIRMED_NEGATIVE) and the same ≥ 5-character justification rule for SKIPPED/CONFIRMED_NEGATIVE. Every change writes a `TASK_STATE_CHANGED` event with `entity_type="task_step"`.
- **Rollup:** a task with active Steps is completed only when all of its active Steps reach a terminal state (COMPLETED, SKIPPED, or CONFIRMED_NEGATIVE). Directly setting a Step-bearing task to COMPLETED while any Step is non-terminal returns **409**. A task with no Steps keeps the original direct status behavior.
- **Verify** evidence at Step level (`POST …/steps/{step_id}/verify`): the verdict, grounded quotations, and extracted assets use the same pipeline as task verification, and the Evidence row links to both the parent task and the Step. In the UI, click **Open** on a Step to reveal its objective, a paste area, **Verify Evidence**, and **Ask Mentor**.
- Once a task has at least one active Step, the task-level verify route returns **409 "this task uses step-level verification"** — verification is owned by the Steps so there is a single source of truth.

### Step-level guidance

Open a Step and use the mentor panel to get Step-scoped guidance. The mentor context then includes the Step's objective, why-it-matters, completion criteria, expected evidence type, and status. Conversations are persisted and reload from the database (§8A).

---

## 6. Scope

### 6.1 Set whitelist / blacklist

**UI (whitelist + lock in one step)**

1. Click **Configure & Lock Scope** under the task tree.
2. In the prompt, enter the authorized target(s), comma-separated, and confirm. The default suggestion is `juice-shop.local`.
3. The UI sends `PUT /api/v1/projects/{project_id}/scope` with the parsed whitelist, an empty blacklist, and rate limit 10, then immediately calls `POST …/scope/lock`.

**API (full control)**

```http
PUT /api/v1/projects/{project_id}/scope
Content-Type: application/json

{
  "in_scope_whitelist": ["juice-shop.local", "10.10.10.0/24"],
  "out_of_scope_blacklist": ["10.10.10.5"],
  "max_rate_limit": 10
}
```

- The whitelist must contain at least one entry and every entry must pass validation.
- The blacklist may be empty; every entry must also pass validation.
- `max_rate_limit` is an integer from 1 to 1000 (default 10).
- Editing a locked scope directly returns **400 "Scope is locked and cannot be modified directly"** — use an amendment (§6.3).

**Valid target formats**

- An IP network (for example `10.10.10.0/24` or `10.10.10.5`).
- A domain-shaped name (for example `app.example.com`).
- The literals `localhost`, `target.local`, and `juice-shop.local`.

Anything else returns **422 "Invalid domain/IP format in whitelist"** (or `…in blacklist`).

### 6.2 Lock the scope

- **UI:** the configure action locks the scope automatically after saving the whitelist.
- **API:** `POST /api/v1/projects/{project_id}/scope/lock`

Rules and effects:

- At least one whitelist target is required, otherwise **400 "Cannot lock scope without at least one in-scope target"**.
- Locking sets `is_locked` and `locked_at`, writes a `SCOPE_LOCKED` audit event with the target list, and updates the header badge to **SCOPE LOCKED**.
- **Evidence verification is blocked while the scope is unlocked** (400), and the Verify Evidence button is disabled.
- After locking, the left-panel button label changes to "Scope locked"; direct reconfiguration is rejected and the supported change path is the amendment flow.

### 6.3 Amend scope

Amendments are the only post-lock mutation path and are permanently recorded.

1. Click **Amend Scope** in the header (enabled only when the scope is locked).
2. Fill in the modal:
   - **Additional target(s), one per line** — each must pass target validation.
   - **Authorizing entity / contact** — required, non-empty.
   - **Justification, minimum 10 characters** — required.
3. Click **Confirm Amendment** (disabled until all three fields are filled).

Server rules (`POST …/scope/amend`):

- Rejected if the scope is not locked (400).
- Invalid target → 422 "Every additional target must be a valid domain or IP".
- Missing authorizer → 422 "authorized_by is required".
- Rationale under 10 characters → 422 "rationale must be at least 10 characters".
- Case-insensitive deduplication against the current whitelist; if every target already exists → **400 "All additional targets are already in scope"**.
- On success: targets are appended to the whitelist, a `ScopeAmendment` row stores only the new targets + authorizer + rationale, and a `SCOPE_AMENDED` audit event is written. The amendment appears in the report's attestation table and in the History drawer.

Amendments only add targets — you cannot remove or edit existing whitelist entries.

---

## 7. Tasks

### 7.1 Selecting a task

- The task tree in the left panel is grouped by phase (Phase 1 through Phase 7). Completed tasks show ✓; all others show ○.
- Click a task to make it active. The right panel shows **ACTIVE TASK**, the title, the objective, and a `<pre>` block with the resolved command.
- Documentation-only tasks have no command template; the block shows the fallback text "Lock scope to resolve command".
- Selecting a different task clears the previous verdict card but keeps your typed evidence until you submit or replace it.

### 7.2 Active Target selector

- The **ACTIVE TARGET** dropdown appears when the scope whitelist is non-empty. The helper text reads: "Commands and scope safety are computed for this target."
- The default is the **first whitelist entry**. Changing the selection refetches tasks with `?target_host=<value>`, so `resolved_command` and `is_scope_safe` are recomputed for that target.
- Any target you request that is not on the whitelist is rejected with **422 "target_host is not within the project scope whitelist"** — commands can never be resolved for an out-of-scope host.
- The selection is UI-only (not persisted server-side). It resets to the first whitelist entry when you switch, create, or import a project; if the stored selection is no longer whitelisted, the UI self-heals to the first entry.

### 7.3 Task statuses

| Status | Meaning |
|---|---|
| `NOT_STARTED` | Default; no evidence or manual progress recorded. |
| `IN_PROGRESS` | Work has begun (manual status change only). |
| `COMPLETED` | Verified evidence returned `PASS` (automatic), or set manually via the API. |
| `SKIPPED` | Deliberately not performed; requires a justification. |
| `CONFIRMED_NEGATIVE` | The objective was to confirm a protective control/missing condition and the evidence positively confirms it; set automatically with the AI summary as justification, or manually with a justification. |

**How statuses change**

- **Automatic (evidence verification, §8.2):** `PASS` → `COMPLETED`; `CONFIRMED_NEGATIVE` → `CONFIRMED_NEGATIVE` with the AI summary stored as the justification. `FAIL` and `AMBIGUOUS` (including the offline/no-key result and the provider-outage fallback) leave the status untouched while still storing the evidence. Only a validated live `PASS` completes a task or Step.
- **Steps:** if a task has active Steps, its status is controlled by Step rollup (§5A) rather than direct transitions, and a direct COMPLETED with non-terminal Steps returns 409.
- **Manual (API):** `POST /api/v1/projects/{project_id}/tasks/{task_id}/state` with `{"status": "...", "justification": "..."}`.
  - Unsupported status → 422 "Invalid task status".
  - `SKIPPED` or `CONFIRMED_NEGATIVE` with fewer than 5 non-space characters of justification → **400 "Justification required"**.
  - Every manual change writes a `TASK_STATE_CHANGED` audit event with `from`, `to`, and the justification.
- **Note:** the current UI does not render status-change buttons. Manual status updates are an API action (for example through `/docs` or a script); the UI only reflects statuses as ✓/○ in the tree.
- Report readiness is stricter than the API: a `SKIPPED`/`CONFIRMED_NEGATIVE` task whose stored justification is under 10 characters produces a WARNING (§11.2).

---

## 8. Evidence

### 8.1 Pasting evidence

1. Select the task the evidence belongs to.
2. Paste the raw tool output into the **Evidence tray** textarea. The placeholder reminds you: "Paste untrusted tool output here. RedSage never executes it."
3. Click **Verify Evidence**.

Controls and limits:

- The button is disabled while the scope is unlocked or the textarea is empty. A capture-phase click guard also disables it immediately on click to prevent double submissions; it re-enables when the request completes.
- Paste between 1 and 2,000,000 characters (`EvidenceSubmit`); surrounding whitespace is stripped before storage.
- Verification is refused with **400 "Cannot verify evidence while scope is unlocked"**; a missing task returns 404.

### 8.2 What happens when you verify

1. The raw text is written atomically to `data/projects/{project_id}/artifacts/{evidence_id}_{timestamp}.txt` **before any AI call** (temp file → flush → fsync → rename), with a 10 MB write cap.
2. An evidence row is created with a random `EVID-XXXXXXXXXX` ID, the repo-relative file path, byte size, SHA-256 digest, and a redacted excerpt (~800 chars) for SQLite.
3. The server clips the log to 80 lines if needed (first 40 + a snip marker + last 40), redacts sensitive patterns, and verifies it against the task objective.
4. Task status is updated from the verdict (§7.3), assets are extracted and upserted (deduplicated by value within the project), keyword-bearing assets can create proposals (§9), and an `EVIDENCE_VERIFIED` audit event is written.
5. The response contains `verdict`, `confidence`, `summary`, `grounded_quotations`, `extracted_assets`, `evidence_id`, and `task_status`.

The verdict card in the UI shows the verdict label, the summary, a **Saved as EVID-…** line with a **View in Evidence Library** shortcut, each grounded quotation as a blockquote, and each extracted asset as a highlighted tag.

### 8.3 Offline mode vs AI available

| Path | When | Verdict behavior | Task effect |
|---|---|---|---|
| Offline deterministic | No `CO_API_KEY` / `COHERE_API_KEY` configured | `AMBIGUOUS` / `LOW`, summary "AI verification unavailable; evidence saved; manual review recommended."; extracts URLs as `ENDPOINT` and absolute paths ending `.zip`/`.env`/`.bak` as `FILE`; first non-empty line is the quotation | Evidence and assets are stored, but the task/Step is **not** completed. Complete manually or with a live key |
| Live Cohere | Key configured, call succeeds | Strict JSON-schema verdict: `PASS`, `FAIL`, `AMBIGUOUS`, or `CONFIRMED_NEGATIVE` with confidence HIGH/MEDIUM/LOW | PASS completes; CONFIRMED_NEGATIVE sets status + justification; FAIL/AMBIGUOUS leave status |
| Provider failure fallback | Key configured but the call fails (429/5xx/network/timeout/malformed) | `AMBIGUOUS` / `LOW`, summary "AI verification unavailable; evidence saved; manual review recommended."; quotations come from the sanitized evidence | Evidence is stored; status unchanged; never HTTP 500 |

In offline mode no evidence leaves the machine. The offline verifier is deterministic and never auto-completes work — it cannot produce PASS, FAIL, or CONFIRMED_NEGATIVE verdicts; those require a live provider (or you can set status manually via the API).

### 8.4 Viewing the Evidence Library

- Open the **Evidence Library (n)** tab to see all artifacts for the project, newest first. The counter in the tab label shows the count.
- Each card shows: the evidence ID, the source task title (and Step title when the evidence is Step-scoped), size in bytes, timestamp, the first 18 characters of the SHA-256 (with **Copy SHA**), a collapsible **Redacted excerpt**, and **View Full Artifact**.
- The search box filters locally across evidence ID, task title, and redacted excerpt.
- **View Full Artifact** opens a modal that fetches `GET /api/v1/projects/{id}/evidence/{evidence_id}/content` and displays the complete raw artifact, with **Copy Content**. Close it with the button or by clicking the backdrop. Errors render the server's error detail or "Artifact unavailable".

Note the modal calls the API on the hardcoded `127.0.0.1:8000` base, like the rest of the UI.

---

## 8A. AI mentor and Boss Brain

**Mentor panel** — click **AI Mentor** for the selected task. Conversations are now **persisted** in SQLite: on open (and after each reply) the panel loads the scoped history from `GET …/tasks/{task_id}/mentor/history` (add `?step_id=` for a Step thread), so the thread survives a page reload.

- Four modes: Teach, Guide, Verify, Summarize.
- Context is bounded to 8,000 characters and includes the task (and Step, when selected), scope, active target, top assets, top confirmed findings, and the latest redacted excerpts. Raw artifacts are never read.
- Without a key or on provider failure the mentor returns a mode-specific static checklist with `ai_available: false`; it never returns HTTP 500.
- User turns are redacted and clipped before storage. The audit event records mode, availability, and question length — never content.

**Boss Brain** — open the **Boss Brain** tab for a read-only project-wide view:

- The left pane shows the active phase/task/Step tree with no state controls.
- The digest shows, per phase, coverage %, asset count, and confirmed-finding count, plus project totals for evidence and confirmed findings. Coverage is computed from the same function Report Readiness uses, so the two never disagree.
- The right pane is a **project-scope conversation** (`POST …/mentor/boss`, history at `GET …/mentor/boss/history`). Ask "what is my status", "what should I prioritize", or "am I ready to report". It answers from measured project data only and is stored separately from task/Step threads.

---

## 9. Proposals (governed follow-up tasks)

### 9.1 Where proposals come from

- **Keyword triggers during verification:** for each extracted asset, if its lowercased value contains `backup`, `admin`, `zip`, `.env`, `config`, or `graphql`, a proposal **"Investigate Exposed Asset: {value}"** is created (priority HIGH, `INVESTIGATION`) unless a proposal for the same `target_asset` already exists in the project. The Refiner selects the target phase; if the provider is unavailable, returns an invalid phase, or is not configured, it safely defaults to Phase 4.
- **Asset-driven suggestions:** in the **Assets** tab, click **Suggest Tasks** on an asset row. Suggestions come from the AI provider when a key is configured (max 2, XML-bounded as untrusted data), otherwise from one safe canned offline proposal; each title is checked against all existing task and proposal titles. The Refiner also proposes a canonical target phase for each suggestion.

### 9.2 Queue rules

- The left panel shows **Proposals (n)** with every PENDING proposal and **Approve** / **Dismiss** buttons.
- The pending queue is capped at **5**. Requesting suggestions when the queue is full returns **400 "Review pending proposals before requesting more"**.
- Duplicate suggestion requests for the same asset + `ASSET_REVIEW` return `{"status": "deduplicated"}` and create nothing; `GET …/proposals` lists PENDING proposals only.

### 9.3 Approve / dismiss / undo

- **Approve** (`POST …/proposals/{id}/approve`): creates a real task in the project phase whose name **exactly matches** the proposal's `phase_name` (set by the Refiner at creation, defaulting to `Phase 4: Vulnerability Analysis`), with `is_ai_proposed: true`, an `order_index` appended after that phase's existing tasks, and the command template `curl -i https://{target_host}/<asset path>`; writes a `PROPOSAL_APPROVED` audit event with the new task ID and target asset. If no phase matches → 400 "No target phase is available for proposed tasks".
- **Dismiss** (`POST …/proposals/{id}/dismiss`): marks the proposal DISMISSED and hides it from the queue. **No audit event is written for a dismissal.**
- **Undo** (`POST …/proposals/{id}/undo`): allowed only when **all** of these hold:
  1. The proposal exists and is APPROVED with a `created_task_id`.
  2. The created task still exists.
  3. The task is untouched — status `NOT_STARTED` and no evidence row references it.

  Otherwise → 400 ("Proposal has no eligible approved task to undo", "Approved task no longer exists", or "Only untouched proposed tasks can be undone"). Undo deletes the created task, returns the proposal to PENDING, clears the link, and writes a `PROPOSAL_UNDONE` audit event.
- In the UI, undo is available through the **History** drawer: an **Undo Addition** button appears only on `PROPOSAL_APPROVED` events that the server currently considers eligible (`can_undo: true`, recomputed on every audit-log fetch).

---

## 10. Findings

### 10.1 Draft vs confirm

- **Draft** — click **+ Log Draft** in the Findings section, enter a title in the prompt (required, 1–300 characters), and confirm. The draft is created with status DRAFT and severity MEDIUM, empty description and reproduction steps, and **no evidence requirement**. If you supply an evidence ID via the API, it must belong to the same project or the request returns **400 "Cannot link draft finding to unknown evidence in this project"**.
- **Confirmed** — drafts are listed under **Drafts (n)** with a **Confirm** button. Confirmed findings are listed separately under **Confirmed (n)** and show their evidence reference (or MISSING). Only confirmed findings enter the report; drafts are ignored by the readiness score.

The panel hint states the rule: "Drafts require no evidence. Confirming requires linked evidence, description, and reproduction steps. Only confirmed findings enter the report."

### 10.2 Confirming a finding (evidence requirement)

1. Click **Confirm** on a draft; an inline form expands.
2. Choose the **evidence** from the dropdown (populated from this project's evidence list; it preselects the draft's evidence or the most recent item). The required evidence must exist **in the same project** — this gate is checked first.
3. Fill in **Title**, **Severity** (dropdown: LOW/MEDIUM/HIGH/CRITICAL; the API also accepts INFO), **Description**, and **Reproduction steps**. **Remediation** and **Affected asset** are optional.
4. Click **Confirm Finding** (or Cancel). Server validation errors render inline in the form.

Confirm endpoint rules (`POST …/findings/{id}/confirm`):

- Unknown finding → 404.
- Already confirmed → 400 "Finding is already confirmed".
- Evidence gate first: missing or cross-project evidence → **422 "Cannot confirm finding without valid linked evidence in this project"**.
- Field gate second: title, severity, description, reproduction steps must be non-empty and severity must be one of LOW/MEDIUM/HIGH/CRITICAL/INFO (stored upper-cased) → otherwise **422 "Cannot confirm finding; missing or invalid: …"**.
- On success: status CONFIRMED and a `FINDING_CONFIRMED` audit event with the evidence ID and severity.

There is no general edit, delete, or un-confirm route; submitting the confirm form is the only way to refine a finding's fields.

---

## 11. Report

### 11.1 Report Studio

- Click the **Report Studio** tab to load the Markdown preview (`GET …/report`). Use **Refresh Preview** to reload it after changes.
- **Download Report (.md)** streams `GET …/report/download` as an attachment; the server names it `redsage_report_{project_name_with_underscores}.md`.
- The report is assembled from database rows only; raw artifacts are never parsed. It contains:
  1. Executive Summary & Posture Overview (status and counts).
  2. Scope & Rules of Engagement Attestation (whitelisted/excluded targets, rate limit, `LOCKED & ENFORCED` vs `UNLOCKED`, and the authorized scope amendments table).
  3. Assessment Methodology & Task Execution Matrix (`| Task | Status | Priority |` for every task).
  4. Target Asset Inventory.
  5. Confirmed Findings only (numbered, `[SEVERITY]`, affected asset, `Evidence Ref: {id|MISSING}`, CWE/CVSS shown as "Not provided", reproduction steps, optional remediation).
  6. Appendix: Evidence Register & Integrity Log.

### 11.2 Readiness panel meaning

The panel next to the preview polls `GET …/report/readiness` and shows a score, a ready flag, the issue list, and per-phase coverage:

- **Score** = `max(0, 100 − 30 × CRITICAL − 10 × WARNING)`; INFO issues are free.
- **Ready for export** is true only when there are **zero CRITICAL** issues; warnings lower the score but do not block export.
- **CRITICAL** — a CONFIRMED finding with missing/invalid linked evidence (blocks export).
- **WARNING** — a confirmed finding with empty reproduction steps or empty remediation; a `SKIPPED`/`CONFIRMED_NEGATIVE` task whose justification is under 10 characters.
- **INFO** — one notice when pending proposals remain unreviewed.
- **Methodology coverage** — per phase, the percentage of tasks with status COMPLETED, SKIPPED, or CONFIRMED_NEGATIVE; empty phases report 0%.

DRAFT findings are not queried by readiness at all: they neither block export nor lower the score.

### 11.3 Evidence register explanation

The final appendix is an integrity log with columns: **Evidence ID | Source Task | Artifact File | File Size | SHA-256 Digest | Timestamp (UTC)**.

- The SHA-256 and size were recorded at save time (and recomputed on import) — the report does not re-hash files at generation time.
- An empty register renders a placeholder row.
- If an artifact file has disappeared from disk, the startup reconciler logs it as CRITICAL; the report itself will still show the recorded metadata. Exporting a project with a missing artifact fails with 409 (§12).

---

## 12. Export and import

### 12.1 Export a project archive

1. Select the project, then click **Export Project** in the header.
2. The UI fetches `GET /api/v1/projects/{project_id}/export`, converts the response to a blob, and downloads `redsage_project_{project_id}.zip`. (The server also suggests a date-stamped filename via `Content-Disposition`.)

Archive contents:

```
manifest.json                 format_version 1.0, exported_at_utc, counts, per-member SHA-256 + size
db/project_data.json          all rows of exactly one project (drafts included), dates ISO-serialized
artifacts/<filename>.txt      every full raw evidence artifact (.txt/.log only)
reports/report.md             report snapshot regenerated at export time
```

- No `.env`, API keys, or other projects are included.
- Limits: archive ≤ 100 MB, ≤ 1,000 members, ≤ 10 MB per member, ≤ 100 MB total uncompressed.
- If an evidence artifact is missing on disk, export returns **409 "Evidence artifact is missing: {id}"**.

### 12.2 Import a project archive

1. Click **Import Project** in the header and choose a `.zip` archive (only `.zip` filenames are accepted).
2. The UI uploads it to `POST /api/v1/projects/import` and shows "Project imported successfully." on success, then reloads the project list and opens the imported project.

What import validates and remaps:

- **Validation:** ZIP member paths must be relative — backslashes, absolute paths, empty/dot segments, and `..` traversal are rejected (zip-slip guard); `manifest.json` must parse with `format_version: "1.0"`; `db/project_data.json` must contain exactly one project; required members and checksums must exist; every checksum is re-verified before anything is written.
- **Remapping:** the project receives a fresh UUID, and so does every scope, amendment, phase, task, **Task Step**, asset, finding, proposal, **mentor message**, and audit event. Evidence IDs are re-minted as `EVID-XXXXXXXXXX`. Foreign keys are rewritten (tasks → phases/project, **Steps → tasks**, assets → tasks, findings → evidence, **evidence → task/Step**, proposals → tasks, mentor messages → project/task/Step, audit `entity_id` and `details` keys `task_id`/`evidence_id`/`proposal_id`). Phase/task/Step archive metadata (`is_archived`, `archived_at`, `archived_by`) is preserved.
- **Artifacts:** written to `data/projects/{new_project_id}/artifacts/{new_evidence_id}_{random}.txt`; `file_path`, `file_size_bytes`, and `sha256_hash` are recomputed from the extracted bytes, while the redacted excerpt and original timestamps are preserved.
- **Findings** keep their exported status (DRAFT or CONFIRMED).
- **Rollback:** any failure rolls back the database transaction and removes only the new project's directory; existing projects and the shared database are untouched.
- Unknown extra keys inside row objects are tolerated; missing required keys fail the import with `400 Invalid project archive: …`. Unknown audit `entity_type` values keep their original `entity_id` by design.

---

## 13. Troubleshooting: top errors and fixes

**1. The UI shows "Failed to fetch" or loads but never talks to the backend (port mismatch).**
The frontend API base is hardcoded to `http://127.0.0.1:8000/api/v1`, and CORS allows only the `5173` dev origins. Run the backend on `127.0.0.1:8000` exactly (`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`). Moving the backend to another port or serving the UI from another origin requires a code change — treat the hardcoded base as a known limitation.

**2. "Cannot verify evidence while scope is unlocked" (Verify button disabled).**
The scope must be locked before any verification. Open **Configure & Lock Scope**, add at least one valid target, and lock it; the header badge should read **SCOPE LOCKED**. The button is also disabled when the evidence textarea is empty.

**3. "Cannot lock scope without at least one in-scope target".**
The whitelist was empty. Save a valid target first; valid formats are IP/IP-network, domain-shaped names, or the literals `localhost`, `target.local`, `juice-shop.local`.

**4. "Invalid domain/IP format in whitelist" (or blacklist).**
One of the comma-separated entries failed validation — fix the spelling/format and retry. Only the three literal hostnames above bypass the domain/IP rules.

**5. "Scope is locked and cannot be modified directly" when trying to edit scope.**
Direct `PUT …/scope` is rejected after locking. Use **Amend Scope** (§6.3): new targets, authorizer, rationale ≥ 10 characters. If the targets are already in scope you will get "All additional targets are already in scope" — nothing to do.

**6. "Justification required" when changing a task status.**
`SKIPPED` and `CONFIRMED_NEGATIVE` need a justification of at least 5 non-space characters at the API layer; report readiness prefers 10 or more (under 10 it raises a WARNING that lowers the readiness score).

**7. "Review pending proposals before requesting more".**
The pending proposal queue is capped at 5. Approve or dismiss existing proposals in the left panel, then retry **Suggest Tasks**.

**8. Confirm finding fails with "Cannot confirm finding without valid linked evidence in this project" or "…missing or invalid: …".**
Select evidence from this project's dropdown (the form auto-selects available evidence), and fill in title, a valid severity, description, and reproduction steps. Drafts are allowed to exist without evidence; confirmation is not.

**9. Export fails with "Evidence artifact is missing: EVID-…" (409).**
A row in the database points to an artifact file that no longer exists under `data/projects/{project_id}/artifacts/`. Restore the file from backup if you have it; otherwise the export cannot include that project row. The startup reconciler logs these as CRITICAL but does not repair them.

**10. Import fails with "Invalid project archive: …".**
The archive failed zip-slip, manifest-version, required-member, or checksum validation, or the filename is not `.zip`. Use an unmodified RedSage export; keep the file under the 100 MB/1,000-member/10 MB-per-member limits. No partial data is written — the failed import rolls back and removes only its new directory.

**11. Root page shows "The built frontend was not found."**
`frontend/dist/index.html` is missing in single-command mode. Run `cd frontend; npm run build`, then reload. Alternatively use dev mode at `http://127.0.0.1:5173`.

**12. Mentor replies "(AI unavailable — static checklist)" or a request fails.**
The API key is unset or the provider call failed; the mentor degrades to a mode-specific static checklist and reports `ai_available: false`. Nothing is lost — retry later. Mentor conversations are persisted per project/task/Step (and per project for Boss Brain), so a page reload restores the thread from the database.

Additional non-blocking warnings you can ignore: the Vite ESM/CJS config warning during builds, and pytest deprecation warnings (FastAPI startup hook, `datetime.utcnow()`, Starlette/httpx/Cohere SDK).

---

## 14. Quick Demo Script (3 minutes)

Everything below uses inert, simulated text. RedSage runs nothing; no scan or exploit is performed. Use only targets you are authorized to test.

**0:00 — Start (single-command mode)**

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

**0:20 — Create the engagement**
Click **+ New Project**, enter `Demo Audit`, confirm. Point out the seven phases and 14 seeded tasks, and the **SCOPE UNLOCKED** badge.

**0:40 — Lock the scope**
Click **Configure & Lock Scope**, enter `juice-shop.local`, confirm. The badge changes to **SCOPE LOCKED**; the Active Target dropdown appears.

**1:00 — Select a task**
Expand **Phase 2: Intelligence Gathering** and select **2.2 Web Content & Directory Discovery**. Note the resolved command is display-only — RedSage will never run it.

**1:20 — Paste simulated evidence and verify**
Paste this inert sample into the Evidence tray and click **Verify Evidence**:

```text
ffuf -u https://juice-shop.local/FUZZ
[Status: 200, Size: 1024]
/backup.zip  [Status: 200, Size: 1048576]
```

(Simulated output; no real target was contacted.)

Because no `CO_API_KEY` is set, the deterministic offline verifier returns **AMBIGUOUS / LOW** with a grounded quotation, extracts `/backup.zip` as a `FILE` asset, and does **not** auto-complete the task (offline verification never completes work). Point out the **Saved as EVID-…** line and that the raw artifact was written to disk before any AI involvement.

**1:50 — Show the Evidence Library**
Open the **Evidence Library (1)** tab: verify the artifact ID, size, SHA-256 (Copy SHA), and redacted excerpt; open **View Full Artifact** to show the full text is stored locally.

**2:10 — Handle the proposal and log a finding**
Back on the Roadmap, find the proposal **Investigate Exposed Asset: /backup.zip**. Click **Approve** to show an audited Phase 4 task appear in the tree (or **Dismiss** to show the other path). Then click **+ Log Draft**, title it `Backup archive exposure`, and click **Confirm** on the draft. In the inline form, select the EVID from the dropdown, choose severity **HIGH**, and fill description and reproduction steps, then click **Confirm Finding**.

**2:40 — Report and export**
Open **Report Studio**: show the readiness score, the coverage bars, and the Markdown including *Confirmed Findings* with the **Evidence Ref** and the *Appendix: Evidence Register & Integrity Log*. Click **Download Report (.md)**, then click **Export Project** to download the checksummed ZIP.

**2:55 — Wrap-up**
Open **History** to show `SCOPE_LOCKED`, `EVIDENCE_VERIFIED`, `PROPOSAL_APPROVED`, and `FINDING_CONFIRMED`. Closing line: every action was executed by the human outside the tool; RedSage only governed, recorded, and reported.

---

*Last verified against version 2.0.0-mvp (UI v2 / V1.1) on 2026-09-10. Ground truth: `EXPLANATION.md` as of 2026-09-08 plus direct reads of `backend/**` and `frontend/src/**`.*
