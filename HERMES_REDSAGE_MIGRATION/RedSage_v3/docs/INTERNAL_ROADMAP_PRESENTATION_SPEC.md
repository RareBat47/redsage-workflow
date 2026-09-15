# RedSage v3 Internal Roadmap Presentation Specification

## Source basis

This specification is derived from the verified RedSage v2 workflow planner UI:

- `frontend/src/components/WorkflowPlannerPanel.tsx`
- `frontend/src/components/TaskStepsPanel.tsx`
- `frontend/src/main.tsx`
- `frontend/src/types/index.ts`
- `frontend/src/planner.css`

The v2 presentation model is retained as a UX reference, but v3 should generate
its roadmap from the new governed KB and v3 domain contracts rather than copy the
v2 component structure wholesale.

## Intended use

This is an internal operator-facing roadmap view for an authorized assessment.
It is not a customer-facing product specification and does not authorize testing.

## Roadmap generation flow

```text
Problem statement
      ↓
Context and authorization review
      ↓
Clarification questions, if required
      ↓
KB retrieval with citations and receipt
      ↓
Roadmap draft
      ↓
Operator review/edit
      ↓
Explicit apply or discard
```

## Presentation model

### Header

Show:

- `INTERNAL WORKFLOW PLANNER`.
- Problem statement title or short label.
- Target type: Web Application, API, or Lab.
- Environment scope.
- Scope status: unknown, unlocked, locked, or blocked.
- Retrieval receipt ID.
- KB/index profile.
- Draft status: clarification required, ready for review, applied, or discarded.

### Safety banner

Always show a prominent state:

- `BLOCKED — authorization or scope clarification required`.
- `READY FOR INTERNAL REVIEW — not yet applied`.
- `LAB-ONLY — do not transfer to real targets`.
- `APPLIED — workflow mutation was explicitly approved`.

The banner must be derived server-side from policy state, not from user-editable
text.

### Clarification panel

When the gate is incomplete, display questions before phases:

1. What exact target is authorized?
2. Who authorized the work?
3. What is explicitly out of scope?
4. What accounts or test data may be used?
5. What rate, time, and operational limits apply?
6. What outcome and evidence standard are required?
7. Is this a real authorized engagement or a lab/CTF environment?

Do not show an actionable roadmap as ready while mandatory clarification remains.

### Roadmap phase cards

Use an expandable phase-card layout similar to v2's `<details>` sections.
Each phase card shows:

- Phase name.
- Phase purpose.
- Why this phase is relevant to the problem.
- Phase status.
- Task count.
- Evidence coverage.
- Warning/stop indicators.
- Source citation count.

Recommended initial phase labels for Web Applications:

1. Context, Authorization, and Scope
2. Application and Attack-Surface Understanding
3. Identity, Authentication, and Session Context
4. Authorization and Object-Access Context
5. Input, Output, and Data-Flow Analysis
6. Business-Logic and Workflow Validation
7. Evidence, Findings, and Reporting

These labels are presentation defaults only; the governed methodology source and
approved v3 methodology version remain authoritative.

### Task cards

Each task card shows:

- Task title.
- Objective.
- Why it matters.
- Priority.
- Preconditions.
- Hypothesis or question being examined.
- Expected evidence type.
- Completion criteria.
- Stop conditions.
- Source citations.
- Current state: not started, in progress, completed, skipped, ambiguous, or
  confirmed negative.

Commands, if ever shown, must be explicitly marked display-only and must never be
executed by RedSage or Hermes.

### Step cards

Each task can expand into ordered Steps, following the useful v2 interaction:

- Step title.
- Objective.
- Why it matters.
- Manual observation target.
- Expected evidence.
- False-positive checks.
- Stop/escalation condition.
- Evidence capture action.
- Ask internal Mentor action.
- Step state.

Task completion should roll up from terminal Steps, preserving the v2 one-source-
of-truth behavior.

### Citation drawer

Each task/Step should expose its supporting citations:

- Citation number.
- Source title.
- Organization/author.
- Source type.
- Version/edition.
- Section/page or locator.
- Source URL or local source path.
- Trust level.
- Content hash.
- Approval/rights notice.

Do not expose a rights-review-required source as if it were approved product
content.

### Review actions

The draft view should provide:

- Edit problem/context.
- Answer clarification questions.
- Regenerate draft.
- Expand/collapse all phases.
- Inspect citations.
- Inspect retrieval receipt.
- Apply as a new workflow.
- Merge with current workflow.
- Discard draft.

Apply and merge require explicit operator action. Viewing or generating a draft
must not mutate the active roadmap.

## Visual behavior borrowed from v2

Retain these useful interaction patterns:

- Planner opens as a modal/panel.
- Clarification questions appear before the draft.
- Draft phases are expandable.
- Tasks are visually nested under phases.
- Steps are opened separately under tasks.
- Nothing changes in the active roadmap until Apply.
- Discard removes only the draft view.
- Busy states prevent duplicate generation/apply actions.

## v3 improvements over v2

Add these fields and states to the presentation:

- Authorization decision.
- Policy decision and filtered-result count.
- Query classification.
- Retrieval receipt.
- Source version and license status.
- Confidence and uncertainty.
- Hypothesis versus observation versus confirmed finding distinction.
- Explicit lab-only handling.
- Stop/escalation reasons.
- Human approval history.
- Draft version and methodology version.

Avoid copying v2 limitations:

- Do not rely on UI-only scope indicators.
- Do not hardcode a seven-phase list into the frontend.
- Do not treat AI output as active workflow state.
- Do not hide filtered or unapproved sources.
- Do not allow a lab roadmap to appear equivalent to a real engagement roadmap.
- Do not expose customer-facing subscription controls in this internal milestone.

## Example internal roadmap display

```text
INTERNAL WORKFLOW PLANNER
Problem: User ID controlled by request parameter
Target: Web application
Environment: LAB ONLY
Status: READY FOR INTERNAL REVIEW
Receipt: qry_...

[Safety] This roadmap applies only to the authorized training lab.

Phase 1 — Context, Authorization, and Scope                 2 tasks
  ✓ Confirm lab scope and supplied account conditions
  ✓ Record allowed objective and stop conditions

Phase 2 — Application and Attack-Surface Understanding       2 tasks
  ○ Establish the normal account-page flow
  ○ Record the identifier-controlled resource request

Phase 3 — Authorization and Object-Access Context             3 tasks
  ○ Form object-authorization hypothesis
  ○ Perform one controlled comparison in the lab
  ○ Capture minimal sanitized evidence

Phase 4 — Validation and False-Positive Review                2 tasks
  ○ Confirm response provenance and account context
  ○ Determine whether access is actually unauthorized

Phase 5 — Evidence and Reporting                              2 tasks
  ○ Map observation to authorization weakness category
  ○ Draft evidence-bounded lab result and remediation note

[Apply to active workflow] [Merge] [Discard]
```

## Acceptance criteria

The v3 internal roadmap presentation is correct when:

- A pasted problem statement produces a readable phase/task/Step hierarchy.
- Mandatory authorization questions appear before technical tasks when needed.
- Every task and Step has objective, evidence, stop-condition, and citation data.
- Draft generation does not mutate active workflow state.
- Apply is explicit and auditable.
- Lab-only context is visibly separated.
- Retrieval receipt and source provenance are visible to the operator.
- No UI action executes a security tool or expands authorization.
