# RedSage v2 Implementation Logic Plan

## 1. Purpose and Planning Basis

This is the codebase-specific implementation plan derived from:

- `REDSAGE_V2_PRODUCT_PLAN.md`, which preserves the supplied Product Plan and milestone plan.
- `WORKSPACE_INVENTORY.md`, which is the repository inventory and identifies the root tree as the live codebase.
- `EXPLANATION.md`, which documents behavior actually implemented on disk.

The root repository is authoritative. Do not copy or modify the stale `GITHUB/` snapshot. Do not build on the legacy `core/` or `interfaces/` KB surfaces. Do not modify `data/chroma/` or hand-edit `frontend/dist/`.

The implementation is intentionally incremental. Each phase is independently testable and must leave the existing application usable before the next phase begins.

## 2. Current-State Findings That Affect Implementation

### 2.1 Runtime shape

- Backend is FastAPI with all live endpoints under `/api/v1`.
- Routers are registered centrally in `backend/main.py`; every new router must be imported and included there.
- SQLAlchemy models are in `backend/models/schema.py`; `Base.metadata.create_all()` creates new tables, but existing SQLite tables require an idempotent migration in `backend/database.py`.
- IDs are application-generated strings: UUID4 strings for most entities and `EVID-XXXXXXXXXX` for Evidence.
- SQLite has no foreign-key pragma enabled. Application-level project/parent validation remains mandatory even when a database FK is declared.
- The live application is single-operator/local-first. No concurrency system should be introduced.

### 2.2 Current workflow shape

- `POST /api/v1/projects` creates a Project, creates an empty Scope, commits, and immediately seeds seven phases and 14 baseline tasks using `seed_project_tasks()`.
- `GET /api/v1/projects/{project_id}/tasks` returns phases and tasks, but no steps.
- `Task` currently has no `steps` relationship.
- Baseline task command templates include safe audit/recon commands in Phases 2 and 4, while Phases 5 and 6 are documentation-only.
- Existing task states are `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`, and `CONFIRMED_NEGATIVE`.
- Manual state transitions require a justification of at least five non-space characters for `SKIPPED` and `CONFIRMED_NEGATIVE`.
- Report readiness applies a stricter ten-character warning threshold. The implementation must preserve this distinction.

### 2.3 Current evidence and AI boundaries

- `POST /api/v1/projects/{id}/tasks/{task_id}/verify` saves the artifact before invoking `verify_task_evidence()`.
- `verify_task_evidence()` owns clipping, redaction, offline fallback, provider fallback, schema validation, and the safe verifier prompt. Do not change its signature or internal ordering.
- The current no-key/offline path returns `PASS`/`MEDIUM`, which can auto-complete a Task. This is unsafe for the new requirements and must be changed to `AMBIGUOUS` with no automatic state transition while retaining artifact persistence and deterministic offline asset extraction.
- Evidence currently has mandatory `task_id` and no `step_id`.
- Assets are deduplicated by `(project_id, value)` and carry a logical `source_task_id`.
- Keyword-derived proposals are created in `evidence.py` and currently force `Phase 4: Vulnerability Analysis`.
- Asset-suggestion proposals are created in `assets.py` and currently force Phase 4 through the service output path.
- `asset_proposal_service.py` catches no provider exception around the live call today. G5 must add safe provider fallback without changing the existing proposal cap/dedup contract.

### 2.4 Current mentor and frontend boundaries

- Mentor context is assembled by `build_context_pack(project_id, task, db, target_host=None)`.
- Mentor requests use the existing safety system prompt and `ask_mentor()` fallback behavior.
- `MENTOR_ASKED` audit events deliberately omit question content.
- Mentor conversations are currently held in a module-level frontend `Map`; there is no persistence API.
- Frontend has one large `App` component in `frontend/src/main.tsx`, a `View` union of four values, and no router library.
- `MentorPanel` currently requires a task and sends to the task mentor endpoint. Step and Boss Brain support must extend it without breaking the current task presentation.
- The frontend API client uses a hardcoded `http://127.0.0.1:8000/api/v1` base. New API calls must use the same helper and route prefix.

### 2.5 Current archive/report boundaries

- Archive export/import explicitly enumerates tables in `backend/services/archive_service.py` and `backend/routers/archives.py`.
- Adding `TaskStep`, `mentor_messages`, and `Project.brief` creates an archive compatibility decision. New rows must not be silently lost in exports of upgraded projects.
- Readiness coverage is calculated inline in `backend/routers/reports.py`; it is not currently a reusable function. Extract the exact existing calculation into a shared service/helper first, then make both readiness and the Boss Brain digest call it. Do not duplicate the calculation.
- The original milestone text says Apply-Replace must not touch evidence/findings. Because deleting Tasks can violate existing evidence relationships and destroy task-linked history, Replace must archive old Tasks/Steps in place, preserving IDs and links, rather than deleting them.

## 3. Global Rules for Every Phase

1. Work only in the root live tree, never `GITHUB/`.
2. Preserve the paste-only human-in-the-loop model. No backend endpoint executes a tool or command.
3. Preserve the established safety prompts, untrusted-data boundaries, redaction, clipping, and deterministic fallbacks.
4. Keep all new AI-authored workflow content visibly proposed until the operator explicitly applies or approves it.
5. Scope-check every project, task, step, and phase lookup at the route boundary.
6. Use one database transaction per mutating request where practical. Roll back on all errors before returning an HTTP exception.
7. Use `db.flush()` before recording references to newly created rows, matching current patterns.
8. New route models should be Pydantic models in `backend/schemas/api_schemas.py`, not untyped request bodies, except where an existing contract must remain unchanged.
9. New tests use `TestClient(app)` and the existing live database/test conventions. Do not weaken existing tests or alter the canonical route contract test except to add new required routes.
10. At every milestone stop gate, run the focused tests, `pytest -m "not e2e"`, and `npm run build` from `frontend/`. Record failures before continuing.
11. Do not commit unless explicitly requested. The milestone plan is commit-sized, but implementation should not create commits autonomously.

## 4. Phase 0A: Proposal Targeting First

This is the first product-code change. Before adding Steps, AI generation, or UI planning, fix ADR-3 so every later discovery/refinement path has a correct destination contract.

### 4.1 Exact targeting rule

In `backend/routers/proposals.py`:

- Replace the current `Phase.name.like("%Phase 4%")` lookup with exact `Phase.name == proposal.phase_name` and `Phase.project_id == project_id`.
- Preserve the existing 400-style error contract for a missing destination, but do not silently route to Phase 4.
- Preserve task insertion order, proposal status, `created_task_id`, `PROPOSAL_APPROVED`, undo eligibility, and the existing safe command-template behavior.

### 4.2 First verification gate

Add the non-Phase-4 approval test before any other feature work:

- Create a project and a proposal targeting `Phase 2: Intelligence Gathering`.
- Approve it.
- Assert the new Task is in Phase 2 and no matching Task appears in Phase 4.
- Assert an unknown phase returns 400 and creates no Task.

Run the existing proposal-related tests immediately after this change. This makes ADR-3 the first implementation checkpoint, not merely the first item in a later combined milestone.

## 5. Shared Contracts to Establish Before Remaining Feature Work

This is a preparatory phase, not a product milestone. It prevents the later phases from duplicating logic or creating incompatible API shapes.

### 5.1 Canonical phase loader

Add one workflow methodology helper, preferably in `backend/services/workflow_engine.py` or a small `backend/services/workflow_contracts.py`, that:

- Loads `data/methodologies/baseline_methodology.json` using a repository-root-safe path rather than depending on the process current working directory.
- Returns the ordered canonical phase names and order indexes.
- Validates a phase name against the exact canonical list.
- Exposes the Phase 4 default as a named constant derived from the canonical list, not a second hardcoded source.

All Planner and Refiner code must use this helper. Existing seeding must continue to use the same file.

### 5.2 Shared state transition helper

Create a small helper, for example `backend/services/task_state.py`, containing:

- `ALLOWED_TASK_STATES`.
- `TERMINAL_TASK_STATES`.
- `validate_state_transition(status, justification)`, preserving current status codes/messages: invalid status is 422 at the route, and insufficient justification is 400.
- A task/step rollup helper that checks sibling Step rows and updates a parent Task only when all siblings are terminal.

The helper must not change existing task endpoint behavior. The current Task route remains the compatibility reference.

### 5.3 Shared readiness coverage helper

Extract the current `reports.py` coverage computation into a pure function, for example:

```python
def calculate_phase_coverage(phases, tasks) -> dict[str, int]:
    ...
```

The first implementation must reproduce the current Task-only result exactly. Before Step support is active, existing tests must remain unchanged. Once Steps exist, define coverage as follows:

- A Task with no Steps contributes its own status.
- A Task with Steps contributes a completed unit only when all its Steps are terminal.
- The denominator remains the number of Tasks in the phase, preserving Report Studio's meaning and preventing a task from counting twice.

Update `reports.py` to call this helper, then make the future digest call the same helper. Add a regression test that old task-only fixtures return the exact prior coverage map.

### 5.4 Archive compatibility policy

Before adding new persisted entities, extend archive row serialization/remapping in a backward-compatible manner:

- Existing archives without `brief`, `task_steps`, or `mentor_messages` must still import.
- New exports include `brief`, `task_steps`, archive metadata, and `mentor_messages` rows and manifest counts.
- Step foreign references remap through task maps and evidence `step_id` maps.
- Mentor messages are metadata/content authored by the operator or AI; preserve their role/mode and remap project/task/step IDs.
- If preserving mentor content in archives is judged unsafe for the existing archive threat model, document and test an explicit exclusion. Do not silently omit it.

This work may be done with G1/G3, but the policy must be decided before the first new table is exported.

### 5.5 Shared test fixtures

Add reusable test helpers only if they reduce duplication without changing production behavior:

- Create and scope-lock a project.
- Select a baseline task.
- Create a task with one or more steps.
- Insert a fixture proposal with a named target phase.
- Patch Cohere success, no-key, failure, and malformed-response paths.

Keep test data safe and non-exploitative.

**Exit criteria:** shared helpers exist where needed, readiness extraction is regression-tested, canonical phase loading is available, and the baseline suite plus frontend build pass.

## 6. Phase G0: Project Brief

**Product mapping:** P0.

**Goal:** Persist an editable project brief without introducing new AI behavior. Proposal targeting is already fixed in Phase 0A.

### 6.1 Backend data and migration

1. Add `Project.brief = Column(Text, nullable=True)` in `backend/models/schema.py`.
2. Add `brief` to the `Project` relationship-free serialization in `projects.py`.
3. Extend `init_db()` with an idempotent `inspect(engine).get_columns("projects")` check and `ALTER TABLE projects ADD COLUMN brief TEXT` for existing SQLite databases.
4. Do not make `brief` non-null. Existing projects and imports must remain valid.

### 6.2 Brief API

Add a Pydantic payload such as `ProjectBriefUpdate` with `text: str`.

- `GET /api/v1/projects/{project_id}` returns `brief` as `null` or a string.
- `PUT /api/v1/projects/{project_id}/brief` trims input, rejects a non-empty value that violates a bounded maximum, and permits an empty string to clear the brief. The supplied plan says "validated non-empty on save but allowed empty by default"; resolve this as: absent/default is empty, while a non-empty update cannot be whitespace-only. Clearing an existing brief is explicitly allowed.
- Unknown project returns the same 404 shape as existing project routes.

### 6.3 Tests

Add tests for:

- Brief default, read, update, trim/reject behavior, and clear behavior.
- A proposal targeting `Phase 2: Intelligence Gathering` being approved into Phase 2.
- A proposal with an unknown phase returning a 400 and creating no task.
- Existing Phase 4 approval, undo, and audit behavior.
- Existing named regression tests: `test_methodology_seeding.py`, `test_workflow_history.py`, `test_assets_pivot.py`.

**Definition of Done:** Brief acceptance criteria pass; full non-E2E suite and frontend build pass; no evidence, mentor, finding, or report behavior is changed except project serialization.

## 7. Phase G1: Task Steps and Manual State Management

**Product mapping:** P1.

**Goal:** Add inert, manually manageable Steps and preserve Task-only compatibility.

### 6.1 Schema and relationships

Add `TaskStep` with:

- `id` string PK.
- `task_id` FK to `tasks.id`, non-null.
- `title` non-null string.
- `objective`, `why_it_matters`, `completion_criteria`, `expected_evidence_type` as non-null Text with safe empty/default handling for manual creation.
- `status` default `NOT_STARTED`.
- `order_index` non-null integer.
- `is_ai_proposed` default `False`.
- `justification` nullable Text.

Add ORM relationships:

- `Task.steps` with `cascade="all, delete-orphan"`.
- `TaskStep.task`.
- `Project` does not need a direct Step relationship unless archive/query use proves it useful; avoid redundant relationships.

Add `Evidence.step_id` nullable FK to `task_steps.id`, with `Evidence.step` and `TaskStep.evidence` relationships. Because the live SQLite database lacks automatic FK enforcement, route-level parent checks remain required.

### 6.2 Migration

- `create_all()` creates `task_steps` and works for fresh databases.
- `init_db()` checks `evidence` columns and adds nullable `step_id` for existing databases.
- Do not make the existing `task_id` nullable or alter its semantics.
- Verify the migration is idempotent by calling `init_db()` multiple times in a test or setup command.

### 6.3 Step API

Add `backend/routers/task_steps.py`, included from `backend/main.py`, with `/api/v1/projects/{project_id}/tasks/{task_id}/steps` routes:

- `GET` returns steps ordered by `order_index`.
- `POST` creates a manual step. Require a non-empty title and bounded text fields; default status `NOT_STARTED`, `is_ai_proposed=False`, and order to append after existing siblings. Validate that the Task belongs to the project.
- `PUT /.../steps/{step_id}` edits text/order fields only. Do not allow an edit to silently change state or AI-proposal history.
- `POST /.../steps/{step_id}/state` accepts the same state payload as Task state. Validate the Step belongs to the requested Task and project.

Every state transition writes `TASK_STATE_CHANGED` with `entity_type="task_step"`, `entity_id=step.id`, and the same `{from,to,justification}` details. The parent Task rollup runs in the same transaction.

### 6.4 Rollup rules

- No Steps: existing Task state route remains unchanged.
- One or more Steps: after a Step state change, if every sibling is terminal, set the Task to `COMPLETED` and record a Task-level `TASK_STATE_CHANGED` event for the rollup.
- If a previously completed Task gains a new non-terminal Step, set the Task to `IN_PROGRESS` only if this is necessary to reflect the new non-terminal work; do not silently overwrite a manually selected terminal state without an audit event. Prefer rejecting creation of a Step under a completed Task unless the task is explicitly reopened, or define and test the reopen behavior before implementation.
- A Task with Steps must not be marked `COMPLETED` through the Task state route unless the route explicitly permits the status and the rollup remains authoritative. The safer v1 behavior is to allow manual Task transitions for backward compatibility but prevent direct completion when non-terminal Steps exist, returning 409. Choose and test one behavior consistently before G2.

### 6.5 Task listing contract

Extend `GET /tasks` with a `steps` array under each Task. Preserve every existing Task key and resolved-command/scope-safety behavior. The frontend can then render steps without a second tree endpoint.

### 6.6 Tests

- Create/list/edit steps under the correct Task.
- Reject cross-project and cross-task Step IDs.
- Exercise all five statuses and the five-character justification gate.
- Verify rollup only after all siblings become terminal.
- Verify `SKIPPED` and `CONFIRMED_NEGATIVE` justification is preserved.
- Verify Task-only state tests remain unchanged.
- Verify task listing still matches existing fields and now includes an empty `steps` array for legacy tasks.
- Verify archive export/import includes or intentionally handles empty/new Step data according to the compatibility policy.

**Definition of Done:** P1 acceptance criteria pass, existing tests remain green, frontend build passes, and no evidence or mentor route is involved yet.

## 8. Phase G2: Step-Level Evidence Verification

**Product mapping:** P2.

**Goal:** Reuse the verifier and asset pipeline at Step scope without creating a second verification implementation.

### 8.1 Refactor shared evidence orchestration

The current evidence endpoint combines artifact persistence, Evidence creation, verification, state mapping, asset upsert, proposal creation, audit, and commit. Extract only the reusable orchestration needed by both Task and Step paths into a helper, for example:

```python
verify_and_persist_evidence(
    project_id,
    task,
    raw,
    db,
    step=None,
    discovery_context=None,
)
```

The helper must call the unchanged `verify_task_evidence(title, objective, raw)` function. Keep the existing task route's response keys and status behavior identical.

### 8.2 Step verify route

Add `POST /api/v1/projects/{project_id}/tasks/{task_id}/steps/{step_id}/verify`:

1. Check scope exists and is locked; return the existing 400 message if not.
2. Check Task and Step parentage/project; return 404 on unknown resources.
3. Save the raw artifact before AI invocation.
4. Create Evidence with `task_id=task.id`, `step_id=step.id`, and the same metadata/excerpt rules.
5. Call `verify_task_evidence(step.title, step.objective, raw)`. Completion criteria are not accepted by the existing verifier signature; include criteria only in future context or a wrapper prompt would violate the explicit constraint. If criteria must affect verification, raise this as an ADR change rather than silently ignoring them.
6. Map PASS to Step `COMPLETED`, CONFIRMED_NEGATIVE to Step `CONFIRMED_NEGATIVE` plus summary justification, and leave Step status unchanged for FAIL/AMBIGUOUS. The no-key/offline verifier result is now `AMBIGUOUS`, so it cannot complete a Step or roll a Task up to completion.
7. Upsert assets with `source_task_id=task.id`, preserving shared dedup behavior.
8. Run discovery proposal logic, initially preserving Phase 4 fallback.
9. Run Step-to-Task rollup, record audit, commit, and return the existing verdict shape plus `step_status` and `task_status`.

The same offline rule applies to the existing Task verification route: when no API key is configured, the persisted evidence result is `AMBIGUOUS` and the Task remains in its prior state. Only a validated live `PASS` can auto-complete a Task or Step.

### 8.3 Task verification guard

At the top of the existing Task verify endpoint, count Steps for the Task. If one or more exist, return HTTP 409 with `this task uses step-level verification`. Do this before saving an artifact so the rejected request has no side effect.

### 8.4 Evidence and listing responses

- Add `step_id` and `step_title` to evidence metadata when available, preserving existing keys.
- Evidence Library search should display the Step title when present and otherwise retain Task title behavior.
- Do not change artifact file naming or redaction/clipping order.

### 8.5 Tests

Mirror the existing verifier tests at Step scope:

- Offline/no-key deterministic `AMBIGUOUS` response, extracted assets, and no Task/Step completion.
- Existing Task-level offline verification also returns `AMBIGUOUS` and does not complete the Task.
- Provider failure -> AMBIGUOUS/LOW, artifact still persisted.
- Mocked live response -> schema shape preserved.
- Malformed response -> safe failure fallback.
- PASS/CONFIRMED_NEGATIVE/AMBIGUOUS state mapping.
- Step evidence appears under the parent Task and Step.
- Asset dedup and source task remain identical.
- Task-level 409 guard has no artifact side effect.
- Unlocked scope rejects Step verification.

**Definition of Done:** P2 acceptance criteria pass and the full regression suite plus frontend build pass.

## 9. Phase G3: Persisted, Step-Aware Mentor

**Product mapping:** P3.

**Goal:** Persist each mentor turn and add Step context without altering safety behavior or fallback semantics.

### 9.1 Mentor message model

Add `MentorMessage` in `schema.py`:

- `id` UUID4 string PK.
- `project_id` FK, non-null.
- `task_id` FK nullable.
- `step_id` FK nullable.
- `mode` string.
- `role` string restricted by route/service to `user` or `assistant`.
- `content` Text non-null.
- `ai_available` nullable Boolean for assistant turns, or an equivalent metadata field if the UI needs to retain fallback labeling.
- `created_at` UTC DateTime.

Add a project relationship and indexes/queries ordered by `created_at`, `id`. Enforce scope combinations in application code: task scope requires task_id; step scope requires both task_id and step_id; project scope has both null.

### 9.2 Mentor context

Extend `build_context_pack(project_id, task, db, target_host=None, step_id=None)` without replacing it.

- When `step_id` is present, load and parent-check the Step.
- Add a `step` object with title, objective, why-it-matters, completion criteria, expected evidence type, and status.
- Filter evidence for the Step where appropriate while retaining parent Task context and bounded excerpts.
- Preserve the 8000-character cap at the final JSON serialization point.
- Keep the existing context when `step_id` is omitted byte-for-byte as much as practical; existing mentor tests must continue to pass.

### 9.3 Mentor routes and persistence

Extend the existing task mentor route to accept optional `step_id` in the request model or add a parallel step route. Prefer a single task route with `step_id` because it keeps existing client behavior and audit scope stable:

- Validate Step parentage before calling the AI.
- Build context with Step fields.
- Call unchanged `ask_mentor()`.
- Persist the user turn and assistant turn after a successful service return, including fallback replies. Store the raw user message only if the product explicitly accepts that sensitive-data persistence risk. The original plan requires persistence, but the current audit policy intentionally omits content. Apply the same `redact_sensitive_data()` and clipping discipline before storage, and document that persisted user content is sanitized.
- Continue writing the existing `MENTOR_ASKED` audit event without question content.

Add `GET /api/v1/projects/{project_id}/tasks/{task_id}/mentor/history?step_id=`. Return ordered normalized messages with UI-friendly `role`, `content`, `mode`, `ai_available`, and `created_at` fields. Unknown or mismatched scope returns 404.

### 9.4 Frontend persistence

Refactor `MentorPanel`:

- Replace the module-level `Map` as the source of truth with a `useEffect` fetch keyed by project/task/step scope.
- Keep optimistic user-message rendering only if failed sends are reconciled safely; otherwise append after API success to avoid duplicate rows.
- Preserve the busy disable and `thinking...` UX.
- Accept an optional `step` prop and send `step_id` when present.
- Keep task-only rendering and existing mode labels.

### 9.5 Tests

- Existing `test_mentor.py` behavior and safety assertions unchanged.
- History contains both sanitized user and assistant turns after offline and live/failure responses.
- A second client/request sees history without the original frontend Map.
- Step context includes completion criteria and expected evidence type.
- Task-only context excludes Step keys.
- Cross-project/task/step history is rejected.
- Archive round-trip covers mentor messages or the documented archive policy.

**Definition of Done:** P3 acceptance criteria pass, mentor safety tests remain green, and frontend build passes.

## 10. Phase G4: Planner Clarification Gate and Workflow Draft, Preview, and Apply

**Product mapping:** P4.

**Goal:** Generate a seven-phase draft from a redacted brief, keep it unpersisted until Apply, and provide deterministic baseline fallback.

### 10.1 Clarification gate contract

The Planner must not immediately generate a workflow from a materially incomplete brief. Implement a deterministic pre-generation gate before both live AI and offline fallback.

Required dimensions should be explicit and bounded, for example:

- Engagement type and target/application context.
- Authorized scope or target description.
- Constraints, exclusions, or safety boundaries.
- Timebox/testing window and relevant rate limits.
- Desired assessment emphasis or reporting outcome.

The gate may use conservative keyword/field presence checks in v1. It must never infer authorization from vague text. If required dimensions are absent, return no draft and a bounded question list. Questions must be methodology-level, safe, and deterministic.

Recommended response envelope:

```json
{
  "status": "NEEDS_CLARIFICATION",
  "questions": [
    {"id": "scope", "question": "What targets are explicitly authorized?"}
  ],
  "draft": null,
  "ai_available": false
}
```

The UI can collect answers into the brief and retry. Do not persist a clarification as a workflow mutation. Do not open a multi-turn Planner chat; the gate is a bounded prerequisite to the one-shot Planner call.

Provide either `POST /api/v1/projects/{project_id}/workflow/clarify` or the same response envelope from `POST /api/v1/projects/{project_id}/workflow/generate`. The second option is smaller and keeps one generation entry point, but the frontend must distinguish `NEEDS_CLARIFICATION` from a generated fallback draft.

### 10.2 Draft schemas

Add Pydantic models in a planner-specific module or `api_schemas.py`:

- `WorkflowStepDraft`: title, objective, why_it_matters, completion_criteria, expected_evidence_type, optional `is_ai_proposed`.
- `WorkflowTaskDraft`: title, objective, optional command_template, priority, steps.
- `WorkflowPhaseDraft`: name, order_index, tasks.
- `WorkflowDraft`: phases.

Use bounded string/list sizes to prevent unbounded provider output. Validate exact canonical phase names, uniqueness of phase names/order, non-empty task titles, and safe command templates. Do not allow generated content to introduce exploit payloads or unsafe automation. A generated `command_template` should be either null or pass a safe allowlist consistent with baseline methodology; the safer v1 option is to omit command templates from AI output and use null for AI-created tasks.

### 10.3 Baseline reshape

Implement a deterministic `baseline_workflow_draft()`:

- Read baseline JSON via the canonical loader.
- Preserve all seven phases, order, task title/objective/priority/command template.
- Create exactly one Step per baseline Task with deterministic safe text:
  - title = task title plus a concise execution/checkpoint suffix, or the task title if title dedup is preferred;
  - objective = task objective;
  - why_it_matters = a static methodology explanation;
  - completion_criteria = a static evidence-oriented criterion;
  - expected_evidence_type = `TERMINAL_LOG` or a safe documentation type accepted by the UI;
  - `is_ai_proposed=False`.
- Keep the baseline fallback stable enough for exact fixture comparison.

### 10.4 Planner service

Implement `planner_service.generate_workflow(brief_text)`:

1. Redact and clip the brief before provider use. Use the existing `redact_sensitive_data()` and a bounded line/character policy.
2. Run the clarification gate. If incomplete, return `NEEDS_CLARIFICATION` with questions and no draft.
3. If neither Cohere key is present and the gate passes, return the baseline reshape and an availability/fallback indicator if the route needs to display it.
4. Prompt the model with the canonical phase list, safe methodology-only constraints, and an untrusted brief boundary.
5. Parse strict JSON into `WorkflowDraft`.
6. Reject invalid phase names, duplicate phases, missing phases, invalid content, malformed JSON, or unsafe command templates. On any provider/schema failure, return the deterministic baseline draft rather than an HTTP 500.
7. Do not silently apply or persist the draft.

The service must distinguish `ai_available` from the draft itself so the UI can explain fallback without treating it as failure.

### 10.5 Workflow routes

Add a router included in `main.py`:

- `POST /api/v1/projects/{project_id}/workflow/generate`: load project/brief, validate project existence, run the clarification gate, and return either questions/no draft or a draft plus availability/fallback metadata. No DB workflow mutation.
- `POST /api/v1/projects/{project_id}/workflow/apply`: payload includes `mode` (`replace` or `merge`) and a validated `draft`.

Apply must be transactional and use `workflow_engine` insertion helpers.

### 10.6 Replace semantics: archive old workflow in place

The old delete behavior is replaced by archive-in-place behavior. Evidence, findings, audit history, proposal links, and report traceability must remain valid.

Add archive metadata to `Phase`, `Task`, and `TaskStep` as needed, preferably:

- `is_archived` Boolean default `False`.
- `archived_at` nullable DateTime.
- `archived_by` nullable String or a fixed system marker such as `planner_replace`.
- For Tasks/Steps, retain existing IDs and all foreign keys. Do not rewrite Evidence `task_id` or `step_id`.

Implement idempotent migrations for these columns. Existing list/read endpoints show active workflow rows by default; provide an internal or explicit `include_archived` query only where audit/history/export requires it.

Replace transaction:

1. Validate the draft and exact canonical phases.
2. Mark all current project Tasks and Steps archived in place, retaining IDs, status, justifications, and relationships.
3. Mark old Phases archived only when the new draft does not use the exact phase name. Reuse matching canonical Phase rows where possible so phase-level joins remain stable; if a new Phase row is required, preserve old archived Phase rows rather than deleting them.
4. Insert new active Tasks and Steps under active matching/new phases.
5. Leave Project, Scope, Evidence, Findings, Assets, WorkflowProposals, MentorMessages, and AuditEvents untouched except for a workflow replacement audit event and explicit archive metadata.
6. Commit atomically. On failure, roll back all archive flags and inserts.

Old tasks remain queryable for evidence/report/audit traceability but are excluded from the active roadmap and active coverage denominator. Report generation must continue to resolve historical evidence source titles; whether archived tasks appear in the methodology matrix must be defined and tested rather than silently changing report meaning.

Approved proposals must not be re-approved into archived rows. New proposal approval always targets an active exact phase. Undo remains available for a newly approved untouched task and must not delete archived historical tasks.

### 10.7 Merge semantics

- For each canonical phase, locate the project phase by exact name.
- If a phase is absent, create it with canonical order only if the draft phase is canonical.
- Compare task titles verbatim among active Tasks within that phase. Archived historical titles do not block a new active task when the new draft intentionally reintroduces the same title.
- For a newly inserted task, insert its Steps in order and set `is_ai_proposed=True` for AI-generated task/step content. Baseline/offline content is false only when directly representing the baseline fallback; Apply of a generated draft should retain the draft flag.
- Do not modify existing Tasks, Steps, evidence, or findings during Merge.

### 10.8 Frontend planner flow

Because there is no router, add planner state and a modal/panel in `main.tsx` or a new component:

- Brief editor with save button.
- Clarification questions shown before generation; answers are appended to or used to revise the Brief.
- Generate button.
- Draft preview showing all seven phases and nested tasks/steps.
- Apply Replace, Apply Merge, and Discard actions.
- Explicit fallback/provider status.
- No draft mutation of the roadmap until Apply succeeds.

Keep the visual language of the existing app while separating preview from live task tree.

### 10.9 Tests

- Incomplete briefs return deterministic clarifying questions and no draft, both with and without an API key.
- Three distinct complete briefs produce visibly different valid task/step trees while retaining the exact seven phases.
- No-key and provider-error paths return the exact deterministic baseline reshape only after the clarification gate passes.
- Invalid phase response falls back safely.
- Brief is redacted before provider prompt.
- Generate does not persist rows.
- Replace archives old Tasks/Steps, preserves old IDs and evidence/findings links, and creates a new active workflow.
- Replace is atomic and preserves counts, hashes, proposal links, audit history, and report traceability.
- Merge deduplicates exact titles and preserves existing records.
- New API routes added to canonical route contract.
- Frontend planner preview/apply build succeeds.

**Definition of Done:** P4 acceptance criteria pass with the clarification gate, deterministic fallback, archive-in-place replacement, and no data loss.

## 11. Phase G5: Discovery-Driven Cross-Phase Refiner

**Product mapping:** P5.

**Goal:** Let the existing discovery pipeline choose a canonical target phase while preserving cap, dedup, approval, undo, and safe fallback behavior.

### 11.1 Proposal schema and service

Extend the proposal AI response model with an optional `phase_name` constrained to canonical names. Preserve existing fields and maximum proposal count.

Refactor `suggest_safe_tasks()` into a generalized service that receives:

- Asset/discovery type and value.
- A compressed project workflow context containing phase names and task titles only.
- The default fallback phase.

The service must:

- Redact asset/discovery text.
- Treat all asset and task-title context as untrusted inert data.
- Return safe proposal objects with validated phase name.
- On no key, provider failure, empty response, malformed JSON, or invalid phase, return the existing deterministic proposal shape targeted to `Phase 4: Vulnerability Analysis`.
- Never produce more than the current max of two service proposals.

### 11.2 Trigger integration

Update both:

- Keyword proposal creation in `backend/routers/evidence.py` or the shared evidence orchestration helper.
- Asset-driven suggestions in `backend/routers/assets.py`.

Run existing pending-count and dedup logic unchanged and before insertion. Pass only the discovered fact plus compressed phase/task-title context into the Refiner. Do not pass raw evidence or unnecessary sensitive project data.

The Step verify route from G2 uses the same helper, so discoveries from Step evidence and Task evidence behave identically.

### 11.3 Approval and safety

G0 exact phase approval is the only approval change. Do not alter proposal approve/dismiss/undo routes, pending cap, or target-asset dedup in G5.

Do not generate a command template from the Refiner that executes or automates an action. Reuse the existing safe proposal insertion behavior, preferably null command templates for new discovery proposals.

### 11.4 Tests

- Mocked Refiner returns Phase 2/5/7 and stored `phase_name` is exact.
- Approval lands in the selected phase.
- Invalid phase/provider/no-key falls back to Phase 4.
- Keyword and Step discovery share dedup and pending cap.
- Existing asset pivot tests remain unchanged and green.
- Proposal undo remains eligible for untouched approved tasks.
- Prompt contains no raw secret after redaction and no exploit-oriented generation instruction.

**Definition of Done:** P5 acceptance criteria pass with existing proposal UI and audit behavior unchanged.

## 12. Phase G6: Boss Brain Dashboard and Digest

**Product mapping:** P6.

**Goal:** Provide a project-wide, read-only status digest and persisted project-scope mentor conversation grounded in the same numbers as Report Studio.

### 12.1 Digest service

Create a pure service, for example `backend/services/workflow_digest.py`, that receives a project and session and returns:

- Ordered phase name/order.
- Coverage percentage from the shared readiness helper.
- Task totals and terminal totals if useful for UI.
- Asset count joined by `source_task_id -> task.phase_id`, with an explicit bucket for evidence-derived/unlinked assets.
- Confirmed finding count joined through finding evidence/task relationships where possible. Current `Finding` has only `evidence_id`, and `Evidence` has Task/Step links, so join through Evidence -> Task -> Phase. Count unlinked confirmed findings in a documented project-level bucket.
- Confirmed findings summary safe for AI context, not raw artifacts.

Add `GET /api/v1/projects/{project_id}/workflow/digest`. It is read-only and has no AI fallback requirement because it makes no provider call.

### 12.2 Readiness parity

Ensure `GET /report/readiness` and digest call the same coverage function. Add a fixture test asserting:

- Digest phase coverage equals `readiness.coverage` exactly.
- Counts are consistent with known assets/findings/evidence.
- Step completion changes both readiness and digest via the same Task rollup semantics.

Do not reimplement readiness scoring inside digest.

### 12.3 Project-scope mentor

Add `POST /api/v1/projects/{project_id}/mentor/boss`:

- Payload uses the existing mentor modes and `user_message` validation.
- Build context from digest, confirmed finding summaries, scope status, asset counts, evidence register counts, and the sanitized user message handled by `ask_mentor()`.
- Reuse `_MENTOR_SYSTEM_PROMPT`, mode directives, clipping, redaction, and fallback from `mentor_service.py`.
- Do not pass raw artifact contents.
- Persist user and assistant turns with `task_id=None`, `step_id=None`.
- Add a project history route, such as `GET /api/v1/projects/{project_id}/mentor/boss/history`, so Boss Brain reloads from SQLite rather than a task history endpoint.
- Continue writing a project-scoped `MENTOR_ASKED` audit event with `entity_type="project"`.

### 12.4 Frontend Boss Brain

Add `boss` to the `View` union and a tab. Create a focused component rather than expanding the already dense JSX beyond maintainability:

- Left pane: read-only phase/task/step tree. Reuse the existing data loaded by `GET /tasks`; no state controls or verify buttons.
- Center/right pane: project-scope `MentorPanel` mode that loads boss history and posts to the boss route.
- Digest cards display exact coverage, asset, finding, and evidence counts.
- Status language must distinguish measured progress from AI recommendations.
- Do not show generated workflow mutations as live; Boss Brain is read-only.

### 12.5 Tests

- Digest route output for empty, task-only, and step-bearing projects.
- Exact readiness coverage parity.
- Asset/finding phase joins and unlinked count behavior.
- Boss mentor no-key and provider-failure HTTP 200 fallback.
- Boss message rows have null task/step IDs and do not appear in task history.
- Task-scoped and project-scoped histories remain distinct after reload.
- Frontend build and route contract pass.

**Definition of Done:** P6 acceptance criteria pass, including a status answer whose context contains the exact Report Studio numbers.

## 13. Cross-Cutting Archive and Migration Completion

This phase is required before release, even if portions were implemented earlier.

### 13.1 Export

Update archive serialization to include:

- `projects.brief`.
- `task_steps`.
- `evidence.step_id`.
- `phases.is_archived`, `tasks.is_archived`, and `task_steps.is_archived` metadata, including archive timestamps/actor where present.
- `mentor_messages` if included by policy.

Update manifest counts and checksums consistently. Existing archives should continue to export/import with missing optional collections represented as empty.

### 13.2 Import

Update ID maps and insertion order:

1. New Project and Brief.
2. Scope/amendments.
3. Phases.
4. Tasks.
5. Steps.
6. Evidence with remapped task/step IDs and rewritten artifact IDs.
7. Assets, findings, proposals, mentor messages, audit events with all supported references remapped.

Do not allow a step from one Task to be imported under another Task. Reject malformed references and roll back the new project directory exactly as existing archive import does.

### 13.3 Regression matrix

Run all existing named tests:

- `test_active_target.py`
- `test_api_contracts.py`
- `test_artifacts.py`
- `test_assets_pivot.py`
- `test_cohere_resilience.py`
- `test_export_archive.py`
- `test_findings_lifecycle.py`
- `test_import_archive.py`
- `test_mentor.py`
- `test_methodology_seeding.py`
- `test_recovery.py`
- `test_report_readiness.py`
- `test_report_traceability.py`
- `test_scope.py`
- `test_scope_amendment.py`
- `test_workflow_history.py`

Then run:

```powershell
pytest -m "not e2e"
```

and:

```powershell
npm run build
```

from `frontend/`.

## 14. Release Acceptance Checklist

### Data and migrations

- Fresh database creates all tables.
- Existing database upgrades idempotently.
- Project Brief is nullable and preserved.
- Evidence remains task-linked and optionally step-linked.
- Archive import/export preserves supported new data and old archives.

### Workflow behavior

- Exactly seven canonical phases are used by baseline, Planner, Refiner, and digest.
- Planner drafts are not live until Apply.
- AI-generated workflow changes are visible and explicit.
- Merge is exact-title deduplication only.
- Replace archives old Tasks/Steps in place and cannot destroy evidence/findings or silently orphan records.
- Task-only workflows remain fully functional.
- Step-bearing Tasks derive completion from terminal Steps.

### AI behavior

- Every AI surface has no-key, provider-error, empty-response, and malformed-response behavior.
- No route returns provider errors as HTTP 500.
- Offline/no-key verifier responses are `AMBIGUOUS` and never auto-complete Tasks or Steps.
- Planner clarification questions block generation until the brief is materially complete.
- Verifier clipping/redaction order is unchanged.
- Mentor safety system prompt is unchanged in substance.
- Prompts treat brief, asset, evidence, task title, and finding text as untrusted data.
- AI never executes tools, marks completion, or applies workflow changes silently.

### Frontend behavior

- Brief editor and Planner preview work on desktop and mobile layouts.
- Steps can be expanded and verified.
- Mentor task/step history survives reload.
- Boss Brain is read-only and project-scoped.
- Proposal target phase is visible and approval lands there.
- Existing Roadmap, Evidence, Assets, and Report views continue to work.

### Verification

- Focused tests pass after each phase.
- `pytest -m "not e2e"` passes with zero new failures.
- `npm run build` passes after each milestone.
- E2E remains optional/deselected unless a running server and browser dependencies are available.
- No changes are made to `GITHUB/`, `core/`, `interfaces/`, Chroma files, generated `frontend/dist/`, or local secrets.

## 15. Recommended Execution Order

1. ADR-3 exact proposal targeting fix and non-Phase-4 approval test.
2. Shared contracts and readiness extraction.
3. G0 Project Brief.
4. G1 Step schema, API, state, rollup, and listing.
5. G2 Step evidence verification, including `AMBIGUOUS` offline behavior and task-level guard.
6. G3 persisted mentor and Step context.
7. G4 Planner clarification gate, draft/preview, and archive-in-place apply.
8. G5 Refiner cross-phase proposal targeting.
9. G6 digest and Boss Brain.
10. Archive/import completion and final regression matrix.

This order makes the proposal-targeting correction the first product change, prevents offline evidence from falsely completing work, preserves historical workflow links through replacement, and forces clarification before Planner output. Shared invariants and the exact Report Studio coverage function are established before later AI/dashboard consumers.
