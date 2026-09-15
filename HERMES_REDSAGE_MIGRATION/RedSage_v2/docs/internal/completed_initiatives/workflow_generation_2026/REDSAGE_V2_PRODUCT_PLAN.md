# RedSage v2: Workflow Generation and Guided Execution

## Document A: Product Plan

### A1. Purpose

This document defines what RedSage v2 must gain: a Brief -> AI Workflow -> Guided Substep Execution -> Adaptive Cross-Phase Proposals -> Boss Brain Dashboard capability, on top of the existing, working, tested base described in `EXPLANATION.md`. It does not specify code. It specifies behavior, data concepts, roles, states, milestones, and acceptance criteria, so that a separate implementation document can be derived from it without ambiguity.

### A2. Non-Negotiable Constraints

- The app never executes tools, scans, or commands. All "execution" is the human pasting real output back in.
- No exploit payloads or step-by-step compromise instructions anywhere in prompts, UI, or generated content.
- Every AI-authored change to the workflow is a proposal: visible, diffed, and requires explicit human approval. No silent edits.
- Local-first, single-operator, single SQLite file. No auth, no multi-user concurrency guarantees.
- Every AI failure mode (no API key, provider error, malformed response) must degrade to a safe, deterministic fallback: never a 500, never data loss, never a stuck state.
- The offline/no-key evidence verifier returns `AMBIGUOUS` and never auto-completes a Task or Step. Offline acceptance of the artifact is not proof that the objective was met.
- Existing, tested functionality (scope lock/amend, evidence pipeline, findings lifecycle, report/readiness, export/import, proposal approve/undo) must remain fully working and fully tested throughout. Nothing in this initiative may regress it.

### A3. What Already Exists vs. What Is New

Already built and must be reused, not rebuilt:

- Evidence verification pipeline (redaction -> clip -> Cohere/offline/failure-fallback -> schema-validated verdict).
- Mentor Q&A with four modes (teach/guide/verify/summarize), scope-aware, injection-resistant.
- Workflow proposal generation (keyword-triggered + asset-suggestion-triggered), with dedup and a pending-queue cap.
- Proposal approve/dismiss/undo with full audit trail.
- Findings draft -> confirm lifecycle gated on evidence.
- Report builder, readiness scoring, evidence register, export/import with integrity checks.

Genuinely new territory:

- A Project Brief field capturing the operator's engagement description.
- An AI Planner role that generates a full seven-phase workflow (tasks + steps) from that brief, replacing the current one-size-fits-all static template as the default path. The static template becomes the offline/no-key fallback shape, not a separate feature.
- A Task Step (substep) entity, one level below Task, with its own objective, completion criteria, expected evidence type, and state.
- Step-level guidance and step-level evidence verification, reusing the existing mentor and verifier pipelines but scoped one level deeper.
- Persistent mentor conversations (currently lost on page reload).
- True cross-phase proposal targeting (currently silently forced into Phase 4 regardless of intent).
- A project-wide "Boss Brain" view: a digest of all seven phases' progress plus a project-scoped mentor conversation, for status/prioritization questions that do not belong to any single task.

### A4. User-Visible Flow

1. Create project -> lock scope (unchanged).
2. Enter a Project Brief (free text: engagement type, constraints, timebox, what is authorized).
3. The Planner runs a pre-generation completeness gate. If the brief is missing material engagement facts, it returns a bounded list of clarifying questions and no workflow draft. The operator answers the questions before generation proceeds. This gate is not a mid-task conversation.
4. Click Generate Workflow -> AI (Planner role) returns a seven-phase draft: phases fixed by name/order, tasks and steps tailored to the brief. Each step carries objective, why-it-matters, completion criteria, expected evidence type.
5. Preview the draft -> Apply (Replace), Apply (Merge), or Discard. Nothing is live until Apply. Replace archives the prior workflow in place; it does not delete old Tasks or break their Evidence links.
6. Enter a phase -> see its active tasks, each expandable into steps. Open a step.
7. Mentor panel (right side), scoped to the step's phase and objective, offers guidance: what to do, what tool category to use, what to capture. Multi-turn: the operator can ask follow-ups if confused or ask about a different tool if the first does not pan out.
8. Operator performs the action manually outside the app and pastes the result.
9. Step Verifier (the existing evidence pipeline, reused) checks sufficiency, returns grounded quotes + extracted assets. Offline/no-key verification is `AMBIGUOUS` and does not complete the Step. Operator sees the verdict and clicks Mark Complete & Continue only after sufficient evidence (explicit action, never inferred from chat text).
10. If the verified result reveals something new and worth acting on, the system automatically raises a cross-phase proposal. For example, a step completed in Phase 2 proposes a new task in Phase 4 or Phase 5. This appears inline in the target phase's task list, visually marked as pending, with one-click Approve/Reject.
11. All of this continuously feeds Findings (draft -> confirm, unchanged) and Report Readiness (unchanged).
12. At any time, the operator can open a Boss Brain view: read-only phase/task tree on the left and a project-wide AI conversation on the right, answering "what's my status," "what should I prioritize," and "am I ready to report," grounded only in real project data (coverage percentage, findings, assets), never inventing progress.

### A5. Roles

There is exactly one underlying AI model, invoked in four distinct roles via different prompts and context:

| Role | Alias in UI | Job | Never does |
|---|---|---|---|
| Planner | "Cohere0 - Planner" | Brief -> full seven-phase draft, after a pre-generation completeness gate | Never guides a human mid-task or silently applies a draft; clarification is bounded and happens before generation |
| Phase Guide | "CohereX - Phase N" | Step-level guidance, multi-turn, answers follow-up questions | Never marks anything complete itself; that is a human button click |
| Verifier | Embedded in the evidence tray, not a chat | Judges sufficiency of pasted evidence against a step's completion criteria | Never invents PASS when evidence is missing or ambiguous; offline mode is always `AMBIGUOUS` |
| Refiner | "Cohere0 - Refine" (invisible; triggered automatically) | Reads a new discovery and proposes where in the seven phases it belongs | Never applies its own proposal; always queued for approval |

Refiner and Planner are the same persona in different modes. Both represent the "boss brain," invoked at different moments (initial planning versus mid-engagement adaptation). The Boss Brain dashboard chat is a third mode of this same persona, scoped to read-only status Q&A rather than generating a workflow diff.

### A6. State Model

ADR-1 (recommended, changeable): Reuse the existing five-value task state enum for Steps too: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`, `CONFIRMED_NEGATIVE`. Do not introduce `NEEDS_EVIDENCE`, `BLOCKED`, or `OUT_OF_SCOPE` as formal states in v1. "Needs more evidence" is just "still `NOT_STARTED`/`IN_PROGRESS` with a verdict shown," and "out of scope" is a filter/flag applied to proposals, not a state a step ever enters. A step that is out of scope should not have been generated; the scope check happens at generation/proposal time, not as a runtime state. This keeps one state machine, one justification rule, and one audit event shape, reused identically at both Task and Step level.

Rollup rule: A Task that has Steps is considered `COMPLETED` only when all its Steps reach a terminal state (`COMPLETED`, `SKIPPED`, or `CONFIRMED_NEGATIVE`). A Task with zero Steps behaves exactly as it does today (state set directly by verify/manual transition). This preserves full backward compatibility with existing projects and existing tests.

### A7. Data Concepts

- Project Brief: one free-text field per project, editable, no versioning required in v1.
- Workflow Draft: a proposed seven-phase/task/step tree, held separately from the live workflow until explicitly applied. Replace archives existing Tasks/Steps in place, preserving their IDs and Evidence links; Merge appends non-duplicate active titles.
- Planner Clarification Gate: a transient, non-workflow response containing bounded questions required before a brief is considered complete enough for draft generation. It is not persisted as a workflow change.
- Task Step: child of Task. Fields: title, objective, why-it-matters, completion criteria, expected evidence type, state, justification, is-ai-proposed flag.
- Mentor Message (persisted): one row per chat turn, scoped to project + task + optionally step, with mode and role (`user`/`assistant`).
- Workflow Proposal (generalized): unchanged shape from today, except the target phase is honored exactly as generated, not silently overridden.
- Digest: a computed, not stored, summary per phase: coverage percentage, discovered assets, confirmed findings. It is assembled from existing data and used only as AI context and dashboard display.

### A8. Product Milestones

| Milestone | Name | Done when |
|---|---|---|
| P0 | Foundation fixes | Cross-phase proposal approval demonstrably lands in a non-Phase-4 phase; Brief field exists and is editable; all existing tests still pass. |
| P1 | Manual Steps | A user can hand-create/edit/transition Steps under any Task; Task rollup works; zero regression on Task-only projects. |
| P2 | Step Verification | Pasting evidence at Step level produces a verdict, grounded quotes, extracted assets, and correctly rolls up to Task completion. |
| P3 | Persistent Step Guidance | Mentor conversations at Step level survive app restart; guidance visibly reflects the Step's own completion criteria, not just the Task's. |
| P4 | AI Workflow Generation | Three different Briefs produce three visibly different, schema-valid, still-seven-phase workflow drafts; Preview/Apply (Replace/Merge)/Discard all work; offline fallback produces the legacy static template. |
| P5 | Discovery-Driven Cross-Phase Proposals | A discovery made in one phase can correctly produce an approvable proposal in a different phase, end-to-end, with existing approve/undo UI unmodified. |
| P6 | Boss Brain Dashboard | A project-wide status question gets an answer grounded in real coverage/findings numbers that match Report Studio exactly. |

### A9. Top Product Risks

- AI invents a phase structure other than the fixed seven. Mitigation: strict schema validation against the known phase list, reject-and-retry on mismatch.
- Cross-phase proposals overwhelm the user. Mitigation: keep one proposal per discovery, respect the existing pending-queue cap, no batch spam.
- Step-level and Task-level evidence paths create two sources of truth. Mitigation: disable direct Task-level verification once a Task has Steps.
- Mentor guidance drifts toward exploit-level detail. Mitigation: apply the same safety system prompt discipline already proven in the existing mentor service to the Planner/Refiner prompts.
- Digest numbers disagree with Report Studio. Mitigation: compute the digest from the exact same functions Report Readiness already uses, never a parallel calculation.
- Solo-development scope creep on Planner "smartness." Mitigation: v1 Merge is title-dedup only, no semantic diffing; explicitly deferred.

## Document B: Incremental Kilo Code Implementation Plan

This document assumes full read access to the existing codebase and to `EXPLANATION.md` (ground truth). Each milestone below is a self-contained changeset. Do not proceed to the next milestone until the current milestone's Definition of Done is met and the full existing test suite (`pytest -m "not e2e"`) still passes at 49+ tests green with zero new failures. Each milestone should be implemented as its own isolated commit/PR. Where a milestone says "reuse X," locate and call the existing function; do not duplicate its logic.

### Recommended ADR Log

- ADR-1: Steps reuse the existing five-value state enum and existing justification-threshold rule (at least five characters), not a new enum.
- ADR-2: Steps live in a new `task_steps` table, FK to `tasks.id`. `evidence.task_id` remains mandatory and unchanged; add a new nullable `evidence.step_id` FK.
- ADR-3: Proposal approval is the first implementation change and must match `Phase.name == proposal.phase_name` scoped to the project, not a hardcoded `%Phase 4%` `LIKE` clause. If the named phase does not exist in the project, fail with the same 400-style error currently used for the missing-Phase-4 case; do not silently reroute.
- ADR-4: The Planner's offline/no-key fallback must be the existing `baseline_methodology.json`, reshaped into one Step per Task. This guarantees the "AI unavailable" story matches every other AI surface in the app: never an error, always a safe deterministic output.
- ADR-5: The Planner/Refiner prompt must list the seven canonical phase names already present in `baseline_methodology.json` and instruct the model that it may only place content under those names. Output is schema-validated against that exact list before acceptance.
- ADR-6: Mentor context-pack building is extended with an optional `step_id` parameter, not replaced with a new service. Reuse `build_context_pack()`'s existing scope/asset/finding logic.
- ADR-7: Offline/no-key evidence verification returns `AMBIGUOUS`, preserves the artifact and extracted offline assets, and never auto-completes a Task or Step. Provider failure remains the existing `AMBIGUOUS`/`LOW` safe fallback.
- ADR-8: Workflow Replace archives existing Tasks and Steps in place using archive metadata while preserving their IDs, Evidence links, findings, audit history, and report traceability. It never deletes old workflow rows.
- ADR-9: Planner generation has a deterministic pre-generation clarifying-questions gate. A materially incomplete Brief returns questions and no draft; no-key mode uses the same gate and only applies the baseline fallback after the gate passes.

### Milestone G0: Un-hardcode Proposal Targeting and Add Brief Field

**Objective:** Fix ADR-3 first, then add the Brief field. No new AI behavior is introduced in this milestone.

**Preconditions:** Full existing test suite green.

**Likely files touched:** `backend/models/schema.py` (add nullable `Text` brief column to Project), `backend/database.py` (extend the existing idempotent migration block with the same reflection + `ALTER` pattern already used for `workflow_proposals.created_task_id`), `backend/routers/proposals.py` (approval logic), and a small route for brief get/set (possibly `backend/routers/projects.py`).

**Exact changes:**

- First, in `proposals.py` approval handler, replace the `phase.name.like("%Phase 4%")` lookup with `Phase.name == proposal.phase_name`, scoped to `project_id`. Preserve the existing 400 error shape/message style for "phase not found," changing only the trigger condition. This is the first product-code change in the entire implementation sequence.
- Second, add the `brief` column via migration, following the exact reflection-check pattern already in `init_db()`.
- Add `brief` to `GET /projects/{id}` response. Add `PUT /projects/{id}/brief {text}` route, rejecting whitespace-only non-empty values while allowing the default/clear value to be empty.
- Add a test creating a proposal with `phase_name="Phase 2: Intelligence Gathering"` and asserting the approved task lands in that phase, not Phase 4. Keep all existing Phase-4-targeting tests passing unmodified; they should still pass because default proposal generators still set `phase_name="Phase 4: ..."`.

**Regression checklist:** Run `test_methodology_seeding.py`, `test_workflow_history.py`, and `test_assets_pivot.py` specifically, plus the full suite.

**Definition of Done:** New test passes; full suite green; brief field readable/writable via API.

**Do not touch:** Evidence pipeline, mentor service, findings, report builder.

### Milestone G1: `task_steps` Table and Manual State Transitions

**Objective:** Introduce Steps as a first-class, manually operable entity (ADR-2), with no AI behavior.

**Likely files touched:** `backend/models/schema.py` (new `TaskStep` model), `backend/database.py` (`Base.metadata.create_all()` creates the table; add `evidence.step_id` nullable column via the existing migration pattern), new `backend/routers/task_steps.py`, and a small shared helper extracted from `tasks.py`'s state-transition validation so Task and Step routes use the same justification-check function per ADR-1.

**Exact changes:**

- Add `task_steps`: `id` (PK), `task_id` (FK `tasks.id`), `title`, `objective`, `why_it_matters`, `completion_criteria`, `expected_evidence_type`, `status` (default `NOT_STARTED`), `order_index`, `is_ai_proposed` (default `False`), `justification` (nullable).
- Extract the existing "is target status valid + is justification present when required" logic from `tasks.py`'s state route into a small shared function such as `validate_state_transition(status, justification)`, used by both the existing task route (behavior-identical refactor) and the new step route.
- Add `GET /projects/{id}/tasks/{task_id}/steps`, `POST /projects/{id}/tasks/{task_id}/steps` (manual create), and `POST /projects/{id}/tasks/{task_id}/steps/{step_id}/state` (mirrors task state route, writes a `TASK_STATE_CHANGED`-style audit event with `entity_type="task_step"`).
- Rollup: when a step's state changes, check whether all sibling steps for that task are terminal. If so, and the task currently has at least one step, set task status to `COMPLETED` and write the same audit event a manual transition would produce.
- Add tests to create steps under a task, transition through all five states with/without justification per the shared validation rule, verify rollup fires only when all steps are terminal, and verify a Task with zero steps behaves identically to before this milestone.

**Definition of Done:** Full existing suite green + new step tests green; refactor of `tasks.py` validation logic is behavior-identical, requiring no changes to existing task-state tests.

**Do not touch:** Evidence verification pipeline, mentor service. Steps are inert text + manual state only at this point.

### Milestone G2: Step-Level Evidence Verification

**Objective:** Reuse `cohere_service.verify_task_evidence()` for Steps.

**Likely files touched:** `backend/routers/task_steps.py` (new verify route), `backend/routers/evidence.py` (reference only; do not duplicate logic from it, call into the same service function it calls), and `backend/models/schema.py` (`evidence.step_id` nullable FK, added in G1 or here if not already done).

**Exact changes:**

- Add `POST /projects/{id}/tasks/{task_id}/steps/{step_id}/verify {raw_content}` with the same request/response shape as the existing task verify endpoint.
- Call `verify_task_evidence()` with the step's title/objective instead of the task's. Confirm by reading `cohere_service.py` that its function signature only needs title/objective/raw text. Do not modify that function's signature; call it with different arguments.
- Persist an Evidence row with `task_id` set to the parent task (inherited for backward-compatible queries) and `step_id` set to this step.
- Change the offline/no-key verifier fallback from the current `PASS` behavior to `AMBIGUOUS`. It must retain the artifact, grounded quote, and safe offline asset extraction but must not auto-complete the Task or Step. Preserve the existing provider-error `AMBIGUOUS`/`LOW` fallback.
- Apply the same scope-lock gate (400 if unlocked) and verdict -> state mapping (`PASS` -> `COMPLETED`, `CONFIRMED_NEGATIVE` -> `CONFIRMED_NEGATIVE` + `justification=summary`) already used at task level, now targeting the step, then trigger the G1 rollup check. `AMBIGUOUS` and `FAIL`, including offline/no-key results, leave the Step and Task state unchanged.
- Once a task has at least one step, make the existing task-level `POST /tasks/{task_id}/verify` route return 409 (`"this task uses step-level verification"`) rather than allowing two parallel state sources.
- Add tests proving step-level verify produces the same verdict/asset/quote shape as task-level, using existing Cohere resilience patterns (offline fallback must be `AMBIGUOUS` with no completion, failure fallback, live mock), proving the 409 guard, and proving assets extracted at step level still upsert into the shared assets table identically. Update any existing offline-verifier assertions that expected automatic completion.

**Definition of Done:** Full suite green; new step-verify tests mirror `test_cohere_resilience.py` coverage (offline/live/failure) at step level.

**Do not touch:** `cohere_service.py` internals; only call it with different arguments.

### Milestone G3: Step-Aware, Persisted Mentor

**Objective:** Implement ADR-6 by extending mentor context to Steps and adding persistence for the known in-memory-only gap.

**Likely files touched:** `backend/services/mentor_service.py` (`build_context_pack()` signature extension), `backend/routers/mentor.py` (accept optional `step_id`), `backend/models/schema.py` (new `mentor_messages` table), a new history route, and `frontend/src/components/MentorPanel.tsx` (replace module-level Map as source with fetched history).

**Exact changes:**

- Add `mentor_messages`: `id`, `project_id`, `task_id`, `step_id` (nullable), `mode`, `role` (`user` or `assistant`), `content`, `created_at`.
- Extend `build_context_pack(..., step_id: Optional[str] = None)`. When provided, include the step's objective, completion criteria, and expected evidence type in the context dict, still respecting the existing 8000-character cap.
- After each successful mentor ask (live or fallback), write both the user and assistant turns to `mentor_messages`.
- Add `GET /projects/{id}/tasks/{task_id}/mentor/history?step_id=` returning the ordered thread.
- In the frontend, fetch history when opening a task/step instead of reading the in-memory Map. Keep the existing thinking UX and busy-disable behavior unchanged.
- Add tests proving mentor history persists across a simulated reload (two separate requests without shared in-memory state) and that the context pack includes step fields when `step_id` is provided while excluding them when omitted.

**Definition of Done:** Full suite green, including all existing `test_mentor.py` cases unchanged in behavior; new persistence + step-context tests pass.

**Do not touch:** Mentor safety system prompt, redaction pipeline, or fallback logic; only context-pack inputs and storage around it.

### Milestone G4: AI Workflow Generation (Planner)

**Objective:** Brief -> seven-phase Workflow Draft -> Preview -> Apply.

**Likely files touched:** New `backend/services/planner_service.py`, new `backend/routers/workflow.py`, `backend/services/workflow_engine.py` (reuse insertion pattern from `seed_project_tasks()`), and `data/methodologies/baseline_methodology.json` (read-only reference, reused as offline fallback shape per ADR-4).

**Exact changes:**

- Implement `planner_service.generate_workflow(brief_text) -> WorkflowDraft`. It builds a prompt listing the seven canonical phase names read from `baseline_methodology.json` (not hardcoded twice) and instructs the model to populate tasks + steps only within that fixed list (ADR-5).
- Define a Pydantic response schema: list of phases; each phase has a name (must match canonical list, validated) and list of tasks; each task has title, objective, and list of steps; each step has title, objective, why-it-matters, completion criteria, expected evidence type.
- Before either live generation or offline fallback, run the Planner clarification gate. If required engagement dimensions are missing, return the questions and no draft.
- Offline fallback (no API key, after the clarification gate passes): reshape `baseline_methodology.json` directly into the same draft schema, one step per existing task, `is_ai_proposed=False`.
- Failure fallback (API error): use the same baseline reshape; do not attempt to accept partial or garbled AI output.
- Add a pre-generation clarification response, either through `POST /projects/{id}/workflow/clarify` or the same response envelope from `POST /projects/{id}/workflow/generate`: `{status: "NEEDS_CLARIFICATION", questions: [...], draft: null}`. Questions must be deterministic and bounded for no-key safety. Generation is blocked until the required answers make the brief complete.
- Add `POST /projects/{id}/workflow/generate`, returning either the clarification response or a draft without persisting it.
- Add `POST /projects/{id}/workflow/apply {mode: "replace"|"merge", draft}`. Replace archives all existing active Tasks and Steps in place, preserving their IDs and Evidence links, then inserts the draft as the new active workflow using the existing phase rows where names match. Merge adds only tasks/steps whose titles do not already exist verbatim among active tasks in that phase (simple string deduplication).
- Redact the brief using `redact_sensitive_data()` before including it in the Planner prompt.
- Add tests for incomplete briefs returning clarifying questions and no draft; three distinct complete briefs producing schema-valid, phase-constrained drafts using mocked Cohere calls; exact offline baseline reshape after the gate; Apply-Replace archiving old tasks while preserving evidence/findings/task IDs; and Apply-Merge avoiding duplicate active titles.

**Definition of Done:** Full suite green; planner tests green; manually generating drafts from three example briefs produces visibly different, valid trees.

**Do not delete or rewrite:** Scope, Evidence, Findings, or Proposal rows during Apply. Replace archives old Tasks/Steps in place and preserves all existing links; only new active phases/tasks/steps are inserted or updated.

### Milestone G5: Discovery-Driven Cross-Phase Proposals (Refiner)

**Objective:** Wire existing discovery trigger points to optionally produce a phase-targeted proposal via AI, using the G0 fix.

**Likely files touched:** `backend/services/asset_proposal_service.py` (generalize to accept/return a phase choice instead of always defaulting to Phase 4), `backend/routers/evidence.py`, and the step-verify route from G2. Reuse the existing `WorkflowProposal` model unchanged.

**Exact changes:**

- Extend the asset-proposal Cohere call schema to include a `phase_name`, constrained server-side to the same canonical seven-name list from G4/ADR-5.
- If the model returns anything outside that list, fall back to `"Phase 4: Vulnerability Analysis"` (today's safe default) rather than rejecting the entire proposal.
- At both discovery trigger points (keyword match in `evidence.py` and the step-verify route), after existing dedup/cap logic runs unchanged, pass the discovered fact + a compressed list of `{phase name, task titles only}` through the generalized service to obtain a phase-targeted proposal instead of using the hardcoded Phase 4 target.
- Do not change proposal approval, dismissal, or undo; G0 makes those phase-agnostic.
- Add a test where mocked AI proposes a phase other than Phase 4, proving it is stored with that `phase_name` and approves into that phase. Keep existing keyword-trigger tests passing because offline fallback still defaults to Phase 4.

**Definition of Done:** Full suite green; new cross-phase proposal test green; existing `test_assets_pivot.py`-style tests unaffected.

**Do not touch:** Proposal approve/dismiss/undo routes, five-pending-cap logic, or existing dedup-by-target-asset logic; only phase selection feeding proposal creation.

### Milestone G6: Boss Brain Dashboard

**Objective:** Read-only project-wide digest + project-scoped mentor conversation.

**Likely files touched:** New `backend/routers/workflow_digest.py`, the coverage-percent function used by `reports.py` readiness (reuse/import, do not reimplement), `mentor_service.py` (project-scope context-pack variant with no `task_id`), and a new frontend tab reusing `MentorPanel` with a project-scope prop.

**Exact changes:**

- Add `GET /projects/{id}/workflow/digest`. It assembles, per phase, the exact coverage percentage calculation already present in the readiness code path, plus counts of assets and confirmed findings joined per phase through existing task -> phase relationships. This is a pure read/aggregate with no AI call.
- Add `POST /projects/{id}/mentor/boss {mode, user_message}`. Build context from digest output + confirmed findings summary + evidence register counts, call the same underlying mentor-ask function used elsewhere (same safety prompt and user-message redaction), and persist to `mentor_messages` with `task_id=NULL`, `step_id=NULL` to distinguish project-scope threads.
- Add a frontend "Boss Brain" tab. Left pane is a read-only phase/task tree using the existing tree-rendering component in read-only mode; right pane is `MentorPanel` pointed at the new route.
- Add tests proving digest numbers for a fixture project match Report Readiness independently for the same project, and proving boss-mentor messages persist under `task_id=NULL` distinctly from task-scoped threads.

**Definition of Done:** Full suite green; digest/readiness cross-check passes; a manual "what's my status" query returns numbers matching Report Studio exactly.

**Do not touch:** Report Studio's own readiness calculation; call it from the new digest route.

## Cross-Milestone Rules

- Do not modify `cohere_service.py`'s core verification function signature or its redaction/clipping order. The one intentional verifier behavior correction is that the no-key/offline fallback is `AMBIGUOUS`, not `PASS`; it must never auto-complete a Task or Step.
- Never remove or weaken the existing five-value state enum, justification threshold rule, or untrusted-data wrapping pattern; reuse them rather than replacing them.
- Every new table follows the existing ID convention (UUID4 strings, or the `EVID-`-style prefix pattern where applicable) and existing idempotent-migration pattern in `init_db()`.
- Every new AI call site must have a defined offline (no-key) behavior and defined failure (provider-error) behavior before the milestone is done. The Planner's no-key path still passes the clarification gate first; the verifier's no-key path is `AMBIGUOUS` with no auto-completion.
- Run `pytest -m "not e2e"` and the frontend build (`npm run build`) at the end of every milestone, not only at the end of the whole plan.
