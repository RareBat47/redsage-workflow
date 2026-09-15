V1 Polish: Governed Scope Amendments, Workflow Audit/Undo, Asset-Driven Pivots, Report Readiness, and Unified Search1. Day-3 Scope: MUST / NICE / NOT TODAY (8–12 Hour Timebox)Day-3 transitions RedSage v2 from a functional prototype into a versatile, engagement-ready workbench. The focus is auditability, pivot flexibility, and deliverable quality—without adding screen bloat or autonomous tool risk.┌─────────────────────────────────────────────────────────────────────────────┐
│                            DAY-3 ARCHITECTURE FLOW                          │
│                                                                             │
│  [Scope Amendment + Audit] ─────────┐                                       │
│                                     ▼                                       │
│  [Assets View] ──(Pivot)──> [Proposals Queue] ──> [Task Workspace]          │
│                                                          │                  │
│  [Global Search] ◄────── [Audit & Undo Engine] ◄─────────┤                  │
│                                                          ▼                  │
│                                            [Report Readiness + Formal Export]│
└─────────────────────────────────────────────────────────────────────────────┘
MUST Build Today (Day-3 Critical Path)Scope Amendment Flow & Audit Trail:Scope remains locked by default."Amend Scope" action: requires new target(s), authorized-by entity, and justification ($\ge 10$ characters).Appends to scope_amendments table and logs a SCOPE_AMENDED event in audit_events.Automatically incorporates a "Scope Amendments & Authorization Log" section into the generated Markdown report.Workflow History & Proposal Undo:Slide-over audit drawer displaying timestamped events (SCOPE_AMENDED, TASK_STATE_CHANGED, PROPOSAL_APPROVED, VERDICT_OVERRIDE)."Undo" action for approved proposals: deletes the auto-created task (if untouched/NOT_STARTED) and resets the proposal to PENDING.Asset-First Pivot (Assets View $\rightarrow$ Governed Tasks):Dedicated Assets View listing extracted hosts, ports, and endpoints."Suggest Tasks for Asset" action on each asset row: sends asset metadata to Cohere (command-r-08-2024) or standard templates to generate 1–2 targeted reconnaissance/auditing proposals in the Proposals Queue.Preserves human governance: tasks are never added directly to the workflow tree; they wait in the queue for user review and approval.Report Readiness Auditor:Slide-out panel or sidebar in Report Studio evaluating report completeness:Flag findings missing linked evidence (CRITICAL).Flag findings missing reproduction steps or remediation (WARNING).Flag tasks marked SKIPPED or CONFIRMED_NEGATIVE lacking required justification (WARNING).Real-time methodology execution coverage (e.g., Phase 2: 100%, Phase 4: 50%).Basic Project-Wide Quick Search:Global search input (Ctrl+K / Cmd+K or header search bar).Queries SQLite for matches across findings.title, findings.description, evidence.redacted_excerpt, and assets.value.Displays max 15 grouped results with immediate navigation to the target item.NICE to Have (If Time Permits in Hours 10–12)Export audit log as CSV or plain-text log from the History drawer.Filter search results by type (Finding, Evidence, Asset).NOT Today (Strictly Deferred)Full-text search (FTS5) over multi-gigabyte disk artifact files (searches DB metadata/excerpts only).Multi-user authorization workflows or digital signatures for scope amendments.Interactive 2D graphical attack-tree canvas.In-app terminal emulation or automated active scanning.2. Implementation MilestonesMilestone 1: Scope Amendment Engine & Report IntegrationUser-Visible Behavior:Header displays [LOCKED] badge with an adjacent [Amend Scope] button.Clicking opens a modal: user enters new target(s), authorizing entity (e.g., "Client Security Lead Jane Doe"), and rationale.Whitelist updates dynamically, command scope checking immediately allows the new target, and the report includes a formal amendment log.Backend Changes:Endpoint: POST /api/v1/projects/{project_id}/scope/amend.Validates new targets via is_valid_target().Appends row to scope_amendments table.Updates scopes.in_scope_whitelist JSON array.Writes to audit_events with type SCOPE_AMENDED.Update backend/services/report_builder.py to render Section 2.1: "Authorized Scope Amendments".Frontend Changes:ScopeAmendModal.tsx: Form component with validation.Update Header.tsx to include "Amend Scope" trigger.Tests: tests/test_scope_amendment.py (validates whitelist expansion, audit entry creation, and rejection of malformed targets).Manual Verification: Amend scope with staging.target.local; verify suggested commands referencing staging.target.local switch from blocked to copyable, and verify the report preview displays the amendment record.Milestone 2: Workflow History & Proposal UndoUser-Visible Behavior:Top navigation contains a [History] button with an event counter.Clicking opens a slide-over drawer displaying chronological project actions.Tasks created via AI proposals display an [Undo Addition] button in the history drawer and on the task card (disabled once evidence is submitted).Backend Changes:Endpoint: GET /api/v1/projects/{project_id}/audit-log.Endpoint: POST /api/v1/projects/{project_id}/proposals/{proposal_id}/undo.Logic: Checks if the task associated with proposal_id has status NOT_STARTED and zero linked evidence. If valid, deletes the Task row, resets WorkflowProposal.status to PENDING, and logs PROPOSAL_UNDONE to audit_events.Frontend Changes:HistoryDrawer.tsx: Slide-over component rendering chronological audit events.Update TaskDesk.tsx to show an "AI Proposed" badge with quick-undo button if task is untouched.Tests: tests/test_workflow_history.py (approves proposal, verifies task creation, executes undo, verifies task deletion and proposal reset).Manual Verification: Approve a /backup.zip proposal $\rightarrow$ verify task appears in Phase 4 $\rightarrow$ click "Undo" in History drawer $\rightarrow$ verify task is removed and proposal returns to pending queue.Milestone 3: Asset-First Pivot & Governed Task GenerationUser-Visible Behavior:Navigation bar includes [Assets] tab.Screen displays discovered assets (Hosts, Ports, Endpoints, Files).Each asset row has a [Suggest Tasks] button.Clicking triggers Cohere to propose 1–2 high-level safe methodology tasks. A notification alerts: "2 new tasks proposed for [Asset] in Proposals Queue".Backend Changes:Endpoint: POST /api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks.Prompt to Cohere (command-r-08-2024): Ingests asset type, value, and current scope rules. Returns max 2 safe, non-intrusive testing tasks conforming to VerificationVerdict or JSON task format.Deduplication: Checks existing tasks and workflow_proposals to prevent duplicate titles for the same target asset.Inserts proposals into workflow_proposals with status PENDING.Frontend Changes:AssetsView.tsx: Data table with filters (Host, Port, Endpoint, File), search bar, and action buttons.Loading spinner on "Suggest Tasks" button.Tests: tests/test_assets_pivot.py (verifies endpoint generates valid proposals and suppresses duplicates).Manual Verification: Navigate to Assets $\rightarrow$ click "Suggest Tasks" on an open port 8080/tcp $\rightarrow$ open Proposals Drawer $\rightarrow$ verify safe enumeration tasks appear $\rightarrow$ approve one $\rightarrow$ verify task appears in Phase 2.Milestone 4: Report Readiness AuditorUser-Visible Behavior:Report Studio displays a dedicated "Report Readiness" panel beside the Markdown preview.Shows overall readiness score (e.g., 85% Ready) and categorized badges:CRITICAL: "Finding VULN-001 has no linked evidence."WARNING: "Finding VULN-002 is missing remediation advice."INFO: "Task 4.2 was SKIPPED without recorded justification."COVERAGE: "Phase 2: 100% complete | Phase 4: 50% complete."Backend Changes:Endpoint: GET /api/v1/projects/{project_id}/report/readiness.Evaluates finding integrity, task justifications, and phase completeness percentages.Returns JSON payload: { ready_for_export: bool, score: int, issues: [...], coverage: {...} }.Frontend Changes:ReadinessPanel.tsx: Accordion/card list with color-coded severity pills (CRITICAL, WARNING, INFO).Direct "Fix" links: clicking an issue jumps directly to the offending Finding or Task.Tests: tests/test_report_readiness.py (verifies flags trigger for unlinked evidence, missing remediation, and incomplete justifications).Manual Verification: Create finding without evidence $\rightarrow$ open Report Studio $\rightarrow$ verify critical warning appears $\rightarrow$ link evidence $\rightarrow$ verify warning clears automatically.Milestone 5: Project-Wide Quick SearchUser-Visible Behavior:Header contains a search input (or press Ctrl+K / Cmd+K anywhere).Modal opens: typing instantly filters Findings, Evidence Excerpts, and Assets.Selecting a result navigates immediately to that entity.Backend Changes:Endpoint: GET /api/v1/projects/{project_id}/search?q={query}.Runs indexed LIKE / parameterized queries across:findings (title, description)evidence (redacted_excerpt, id)assets (value, type)Returns grouped results capped at 5 per category.Frontend Changes:SearchModal.tsx: Global keyboard-accessible search dialog with highlighted match snippets.Tests: tests/test_search.py (verifies search returns matching findings, evidence excerpts, and assets).Manual Verification: Press Ctrl+K $\rightarrow$ search for "backup" $\rightarrow$ click matching Evidence item $\rightarrow$ verify Evidence Library opens directly to that artifact.3. Exact UX Behaviors & Screen Contracts3.1 Scope Amendment Flow┌────────────────────────────────────────────────────────────────────────┐
│                        AMEND AUTHORIZED SCOPE                          │
├────────────────────────────────────────────────────────────────────────┤
│ Active Whitelist: target.local, 192.168.1.50                           │
│                                                                        │
│ Additional Target(s) (One per line):                                   │
│ [ api.target.local                                                   ] │
│ [ staging.target.local                                               ] │
│                                                                        │
│ Authorizing Entity / Contact:                                          │
│ [ Client SecOps - Jane Doe (Ticket SEC-4091)                         ] │
│                                                                        │
│ Amendment Justification (Min 10 characters):                           │
│ [ Discovered staging subdomain during passive DNS enumeration.       ] │
│ [ Client confirmed in-scope via email.                               ] │
│                                                                        │
│ [!] Notice: This change will be permanently recorded in the audit trail │
│     and documented in the final report's Scope Amendment Register.     │
│                                                                        │
│             [ Cancel ]                  [ Confirm Amendment ]          │
└────────────────────────────────────────────────────────────────────────┘
Default State: Locked. The inputs in the initial Scope Wizard remain read-only.Validation Rules:Additional targets must pass is_valid_target().Authorizing entity cannot be empty.Justification must be $\ge 10$ characters.Post-Submit State:Whitelist immediately expands in application memory.Toast notification: "Scope amended: 2 targets added. Audit event recorded."Generated commands targeting the newly added hosts transition from BLOCKED to copyable.3.2 Workflow History & Proposal Undo┌────────────────────────────────────────────────────────────────────────┐
│                        PROJECT AUDIT & HISTORY                         │
├────────────────────────────────────────────────────────────────────────┤
│ [Filter: All Events ▼]                              [Export Audit Log] │
│                                                                        │
│ • 11:42 UTC | PROPOSAL APPROVED                                        │
│   Task: "Investigate Exposed Asset: /backup.zip" added to Phase 4.     │
│   Target: target.local/backup.zip                                      │
│   [ Undo Addition ]                                                    │
│                                                                        │
│ • 11:35 UTC | EVIDENCE VERIFIED                                        │
│   Task 2.2 marked COMPLETED. Status: PASS (Confidence: HIGH)           │
│   Artifact: EVID-002 (SHA-256: 4a8b1c...)                              │
│                                                                        │
│ • 11:20 UTC | SCOPE AMENDED                                            │
│   Added: api.target.local | Authorized by: Jane Doe                    │
│   Reason: Discovered during recon; client approved via email.          │
│                                                                        │
│ • 11:00 UTC | SCOPE LOCKED                                             │
│   Initial scope confirmed for target.local.                            │
└────────────────────────────────────────────────────────────────────────┘
Undo Eligibility Rule: An [Undo Addition] button is visible only if:The task was created from an AI proposal (is_ai_proposed == True).The task status is still NOT_STARTED.No evidence records are linked to the task.Undo Action Result:The task is deleted from tasks.The corresponding workflow_proposals record resets to PENDING.An audit event PROPOSAL_UNDONE is appended.Toast alert: "Task removed and returned to Proposals Queue."3.3 Asset-First Pivot: "Suggest Tasks" Flow┌───────────────────────────────────────────────────────────────────────────────────────┐
│                              DISCOVERED TARGET ASSETS                                 │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ [Filter: All (12) ▼]  [Search Assets...]                       [+ Manually Add Asset] │
├──────────┬──────────────────────────┬──────────────────┬──────────────────────────────┤
│ Type     │ Asset Identifier         │ Source Task      │ Actions                      │
├──────────┼──────────────────────────┼──────────────────┼──────────────────────────────┤
│ HOST     │ target.local             │ 2.1 Port Scan    │ [ Suggest Tasks ] [ Evidence]│
│ PORT     │ 8080/tcp (Apache Tomcat) │ 2.1 Port Scan    │ [ Suggest Tasks ] [ Evidence]│
│ ENDPOINT │ /rest/user/login         │ 2.2 Web Content  │ [ Suggest Tasks ] [ Evidence]│
│ FILE     │ /backup.zip              │ 2.2 Web Content  │ [ Suggest Tasks ] [ Evidence]│
└──────────┴──────────────────────────┴──────────────────┴──────────────────────────────┘
User Action: Clicks [Suggest Tasks] on PORT: 8080/tcp (Apache Tomcat).Backend Processing:Checks pending proposals to prevent duplicates.Calls Cohere command-r-08-2024 with prompt:"Propose 1-2 safe, standard verification tasks for Apache Tomcat on port 8080. DO NOT provide exploits. Format as JSON."Writes proposed items to workflow_proposals with status = "PENDING".UI Outcome:Header Proposal Badge updates: Proposals (3).Toast notification: "2 new tasks proposed for 8080/tcp in Proposals Queue."The user opens the Proposals Drawer to review, accept, or dismiss. No tasks are forced into the workflow automatically.3.4 Report Readiness Panel┌────────────────────────────────────────────────────────────────────────┐
│                       REPORT READINESS AUDITOR                         │
├────────────────────────────────────────────────────────────────────────┤
│ Overall Readiness: 78% (3 Actionable Warnings)                         │
│ [■■■■■■■■■■■■■■■■■■■□□□□□]                                             │
├────────────────────────────────────────────────────────────────────────┤
│ ⛔ CRITICAL (Must fix before client export)                            │
│ • Finding "SQL Injection in Search": Missing linked evidence.          │
│   [ Link Evidence ]                                                    │
│                                                                        │
│ ⚠️ WARNINGS                                                            │
│ • Finding "Exposed Backup Archive": Missing remediation advice.        │
│   [ Edit Finding ]                                                     │
│ • Task "4.2 Auth Surface Analysis": Marked SKIPPED without reason.     │
│   [ Add Justification ]                                                │
│                                                                        │
│ 📊 METHODOLOGY COVERAGE                                                │
│ • Phase 2: Intelligence Gathering ──── 100% (2/2 Tasks Completed)      │
│ • Phase 4: Vulnerability Analysis ────  50% (1/2 Tasks Completed)      │
└────────────────────────────────────────────────────────────────────────┘
Readiness Evaluation Logic:Critical: Any finding marked CONFIRMED without an associated evidence_id.Warning: Any confirmed finding with empty reproduction_steps or remediation.Warning: Any task marked SKIPPED or CONFIRMED_NEGATIVE with justification < 10 chars.Informational: Unreviewed proposals remaining in the Proposals Queue.3.5 Project-Wide SearchShortcut: Ctrl+K or Cmd+K toggles modal from any screen.Query Behavior: Matches against findings.title, findings.description, evidence.redacted_excerpt, and assets.value.Latency & Budget: Runs against local SQLite via parameterized SQL LIKE queries. Zero Cohere API calls consumed.Navigation: Pressing Enter or clicking a result closes the modal and switches directly to the target tab (Findings, Evidence Library, or Assets).4. Risks, Safeguards, and MitigationsFailure Mode / RiskImpactProduct & UX SafeguardTechnical Mitigation1. Accidental Scope Drift via AmendmentsOperator enters a typo'd or unauthorized domain during an amendment (e.g., google.com), generating commands against external third parties.Amendment requires an explicit confirmation modal displaying the target list, authorized-by contact, and legal acknowledgement before saving.is_valid_target() enforces strict FQDN/IP syntax. Client-side regex prevents wildcard subnets (0.0.0.0/0) or common cloud metadata endpoints (169.254.169.254).2. Workflow Bloat from Asset SuggestionsOperator clicks "Suggest Tasks" on 15 assets, flooding the task tree with dozens of redundant tasks.The system caps total pending proposals to 5 items max. Tasks are never auto-added to the roadmap; operator must manually approve each item.Proposal deduplication engine hashes project_id + target_asset + action_type to discard duplicate suggestions.3. Token Exhaustion on Asset SuggestionsRepeatedly querying Cohere for asset-based tasks burns through API credits.Asset suggestions are constrained to a strict prompt returning a max of 2 short task objects.Caches generated proposals for identical assets; limits asset suggestion queries to 1 call per asset per hour.4. Incomplete Deliverables ExportedOperator exports an unreviewed report with missing evidence citations or blank reproduction steps.Report Studio displays the sticky Report Readiness Panel with prominent red warning badges.While export is not hard-blocked (giving the tester final say), the export modal displays an alert: "Report has 2 critical integrity warnings. Export anyway?"5. UI Overwhelm & Navigation SprawlAdding more features creates tab confusion and cognitive fatigue for the solo tester.Retains a strict 4-tab top navigation bar: [Roadmap] [Assets] [Evidence Library] [Report Studio].Search, History, and Scope Amendments operate as transient slide-over drawers or modals rather than dedicated persistent screens.5. The Kilo Code Prompt (Single Paste for Day-3 Execution)Copy and paste the prompt below into your VS Code coding agent to run the entire Day-3 build autonomously:MarkdownYou are an elite software architect and full-stack engineer upgrading "RedSage v2" for Day-3: Scope Amendments, Workflow History & Undo, Asset-Driven Pivots, Report Readiness, and Unified Search.

OBJECTIVE:
Complete all Day-3 milestones sequentially. At the end of this session, RedSage v2 will feature:
1. A governed Scope Amendment flow with audit logging and report integration.
2. A Project History drawer with one-click Undo for approved proposals.
3. An Assets View where clicking an asset generates safe task proposals into the Proposals Queue.
4. A Report Readiness panel flagging missing evidence, reproduction steps, or justifications.
5. A global Ctrl+K search dialog querying findings, evidence excerpts, and assets.

CRITICAL CONSTRAINTS (NON-NEGOTIABLE):
1. PRESERVE `core/`: DO NOT modify, delete, or touch any files in `core/` (config.py, embeddings.py, kb_engine.py) or `data/chroma/`.
2. HUMAN-IN-THE-LOOP: The app must NEVER run security tools or network scans directly.
3. NO EXPLOIT PAYLOADS: Keep all command suggestions strictly high-level and safe (recon/auditing).
4. UNTRUSTED DATA & REDACTION: Continue clipping logs (max 80 lines) and regex-redacting secrets in memory before sending to Cohere.
5. GOVERNED ADAPTATION: Tasks generated from assets MUST go to `workflow_proposals` with status `PENDING`. NEVER inject tasks directly into the workflow without human approval.
6. PROGRESS TRACKING: Update `PROGRESS.md` after completing each milestone.

EXECUTE THESE MILESTONES IN SEQUENCE:

### Milestone 1: Scope Amendment Engine & Report Integration
1. Backend (`backend/routers/scope.py`):
   - Implement `POST /api/v1/projects/{project_id}/scope/amend` accepting `{ "additional_targets": ["api.target.local"], "authorized_by": "Jane Doe", "rationale": "Discovered via recon" }`.
   - Validate each target with `is_valid_target()`. Reject if malformed.
   - Append targets to `scopes.in_scope_whitelist`.
   - Insert row into `scope_amendments` table.
   - Insert row into `audit_events` with `event_type = 'SCOPE_AMENDED'`.
2. Report Builder (`backend/services/report_builder.py`):
   - Update `build_markdown_report()` to include Section 1.1: "Authorized Scope Amendments" (table: Date, Added Targets, Authorized By, Rationale).
3. Frontend:
   - Create `frontend/src/components/ScopeAmendModal.tsx`.
   - Add an [Amend Scope] button next to the scope badge in `frontend/src/components/Header.tsx`.

### Milestone 2: Workflow History & Proposal Undo
1. Backend:
   - Create `backend/routers/audit.py` with `GET /api/v1/projects/{project_id}/audit-log` returning sorted `audit_events`. Register router in `main.py`.
   - Update `backend/routers/proposals.py`: add `POST /proposals/{proposal_id}/undo`.
     - Rule: If the created task has `status == 'NOT_STARTED'` and no linked evidence, delete the task, set `proposal.status = 'PENDING'`, and record `PROPOSAL_UNDONE` in `audit_events`. If task is already completed or has evidence, return HTTP 400.
2. Frontend:
   - Create `frontend/src/components/HistoryDrawer.tsx` displaying chronological audit events with an [Undo Addition] button for eligible proposals.
   - Add a [History] toggle button in `frontend/src/components/Header.tsx`.

### Milestone 3: Asset-First Pivot & Governed Task Generation
1. Backend (`backend/routers/assets.py`):
   - Add `GET /api/v1/projects/{project_id}/assets`.
   - Add `POST /api/v1/projects/{project_id}/assets/{asset_id}/suggest-tasks`:
     - Calls Cohere `command-r-08-2024` with prompt: `"Suggest 1-2 standard, non-intrusive auditing/reconnaissance tasks for asset: {asset.value} (Type: {asset.type}). DO NOT provide exploits or attack payloads. Return JSON list matching schema: [{title, objective, command_template, priority}]."`
     - Deduplicate against existing tasks and pending proposals.
     - Insert proposals into `workflow_proposals` with `status = 'PENDING'`.
2. Frontend:
   - Create `frontend/src/pages/AssetsView.tsx`: Table listing assets (Type, Value, Source Task) with search filter and a [Suggest Tasks] button per row.
   - Update `App.tsx` navigation to include the [Assets] tab.

### Milestone 4: Report Readiness Auditor
1. Backend (`backend/routers/reports.py`):
   - Add `GET /api/v1/projects/{project_id}/report/readiness`:
     - Checks confirmed findings for missing evidence or empty reproduction/remediation.
     - Checks skipped/confirmed-negative tasks for empty justification.
     - Calculates completion percentages per phase.
     - Returns `{ ready_for_export: bool, score: int, issues: [{ severity, message, entity_type, entity_id }], coverage: { phase_name: percentage } }`.
2. Frontend:
   - Create `frontend/src/components/ReadinessPanel.tsx`.
   - Embed this panel beside the Markdown preview in `frontend/src/pages/ReportStudio.tsx`.

### Milestone 5: Project-Wide Quick Search
1. Backend (`backend/routers/search.py`):
   - Implement `GET /api/v1/projects/{project_id}/search?q={query}`:
     - Search `findings` (title, description), `evidence` (redacted_excerpt, id), and `assets` (value).
     - Return grouped JSON list capped at 5 results per category.
2. Frontend:
   - Create `frontend/src/components/SearchModal.tsx` accessible via `Ctrl+K` / `Cmd+K` or search icon in header.
   - Clicking a result navigates directly to that Finding, Evidence item, or Asset.

### Milestone 6: Automated Testing & Build Verification
1. Create tests:
   - `tests/test_scope_amendment.py`: Test amendment whitelist updates and audit logging.
   - `tests/test_workflow_history.py`: Test proposal approval and subsequent undo.
   - `tests/test_assets_pivot.py`: Test asset task suggestion and deduplication.
   - `tests/test_report_readiness.py`: Test readiness auditor issue detection.
   - `tests/test_search.py`: Test parameterized project search.
2. Run `pytest tests/` and ensure all tests pass (100% green).
3. Run `npm run build` in `frontend/` and ensure zero TypeScript or bundling errors.
4. Update `PROGRESS.md` with completed milestones.
5. Output a final summary of Day-3 deliverables and instructions to run and test.

Begin Milestone 1 now. Proceed through each milestone autonomously, resolving errors as they arise.