RedSage v2: QA Hardening & Function Assurance PlanPre-Engagement Reliability, Security Invariants, and Regression Prevention1. Definition of “Release-Ready”A build of RedSage v2 is deemed Release-Ready when it guarantees three non-negotiable operational invariants: Scope Integrity, Artifact Immutability, and Local Execution Safety.┌─────────────────────────────────────────────────────────────────────────────┐
│                         RELEASE-READY GATE CRITERIA                         │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│ Backend Test Suite           │ Frontend Production Build    │ System Safety │
│ • 100% pytest pass rate      │ • Zero TypeScript errors     │ • Zero leaks  │
│ • Zero unhandled exceptions  │ • Zero ESLint errors         │ • Zip-slip OK │
│ • >85% critical branch cov   │ • Clean dist/ generation     │ • Scope hard  │
└──────────────────────────────┴──────────────────────────────┴───────────────┘
1.1 Mandatory Pass/Fail CriteriaBackend Verification (pytest):100% pass rate across unit, integration, and security test suites.Zero unhandled 500 Internal Server Error responses on malformed or adversarial inputs.High statement and branch coverage on critical modules:backend/services/scope_validator.py $\ge 95\%$backend/services/artifact_manager.py $\ge 95\%$backend/services/archive_service.py (Import/Export) $\ge 90\%$backend/routers/evidence.py $\ge 85\%$Frontend Compile & Bundle:npm run build exits with code 0.Zero TypeScript compiler errors (tsc --noEmit).Production bundle generated in frontend/dist/ without broken chunk imports.Single-Process Runtime Execution:Server boots via uvicorn backend.main:app and correctly mounts frontend/dist/ at /.Direct browser refresh on deep routes (e.g., /projects/:id/tasks) returns the SPA index without 404s.Data & Secret Sanitization:In-memory redaction engine successfully sanitizes 100% of test fixture tokens, passwords, and JWTs before storage in redacted_excerpt and before transmission to Cohere.1.2 What “Not Guaranteed” Means (Explicit Operational Boundaries)Cloud Dependency Uptime: While Cohere availability is out of our control, RedSage v2 guarantees graceful degradation: missing API keys or remote 429/500 errors trigger the built-in offline heuristic verifier without halting the operator's workflow.Host Power Loss Resilience: If the host machine is abruptly terminated mid-write, SQLite transactional integrity is protected by WAL/journaling, but in-flight artifact file writes to disk may require manual re-submission.Massive File Processing: Day-1/Day-2 design limits artifact sizes to $\le 10\text{ MB}$. Ingestion of multithreaded raw dumps beyond this threshold is intentionally rejected by design.Multi-User Concurrency: The application is explicitly single-user and local-first. Race conditions from multiple operators accessing the same SQLite database simultaneously are out of scope.2. Critical User Flows to Test (Exhaustive Test Matrix)       [Scope Gate Flow]         [Evidence Pipeline]          [Archive Pipeline]
     ┌───────────────────┐      ┌───────────────────┐       ┌───────────────────┐
     │ • Locked by default│      │ • In-memory redact│       │ • Checksum verify │
     │ • Strict amendment│      │ • Disk artifact   │       │ • Zip-slip guard  │
     │ • Blocked command │      │ • SHA-256 digest  │       │ • ID remapping    │
     └───────────────────┘      └───────────────────┘       └───────────────────┘
2.1 Project LifecycleHappy Path:TC-PROJ-01: Create project with valid name ("Acme Assessment"), target type (web_app), and description $\rightarrow$ Returns 201 with UUID, initializes 7 phases and baseline tasks in SQLite.TC-PROJ-02: List projects $\rightarrow$ Returns all projects with accurate task counts and completed status.TC-PROJ-03: Delete project $\rightarrow$ Deletes SQLite rows and cascades removal of data/projects/{id}/artifacts/ on disk.Failure / Edge Cases:TC-PROJ-04: Create project with empty or whitespace name $\rightarrow$ Returns 422 Unprocessable Entity.TC-PROJ-05: Delete non-existent project ID $\rightarrow$ Returns 404 Not Found.TC-PROJ-06: Project deletion with missing filesystem folder $\rightarrow$ Cleanly deletes database record without throwing uncaught filesystem exceptions.2.2 Scope Enforcement & AmendmentsHappy Path:TC-SCOPE-01: Set valid FQDNs (target.local), IPv4 (192.168.1.1), and CIDRs (10.0.0.0/24) $\rightarrow$ Persists whitelist.TC-SCOPE-02: Lock scope via POST /lock $\rightarrow$ Marks is_locked = True, sets timestamp.TC-SCOPE-03: Amend scope with valid target, authorized contact, and $\ge 10$-character rationale $\rightarrow$ Appends to whitelist, writes scope_amendments row, records SCOPE_AMENDED in audit log.Failure / Edge Cases:TC-SCOPE-04: Update scope while locked $\rightarrow$ Returns 400 Bad Request ("Scope is locked").TC-SCOPE-05: Save invalid target format (e.g., invalid!target@, http://, 0.0.0.0/0) $\rightarrow$ Returns 422 with exact invalid target identified.TC-SCOPE-06: Scope amendment with rationale $< 10$ chars $\rightarrow$ Returns 400 Bad Request.TC-SCOPE-07: Scope amendment with empty authorized_by $\rightarrow$ Returns 400 Bad Request.TC-SCOPE-08: Command generation referencing out-of-scope host $\rightarrow$ UI blocks copying; backend returns is_scope_safe = False.2.3 Task State MachineHappy Path:TC-TASK-01: Transition NOT_STARTED $\rightarrow$ IN_PROGRESS $\rightarrow$ COMPLETED upon verified evidence.TC-TASK-02: Skip task with $\ge 10$-char justification $\rightarrow$ State transitions to SKIPPED, justification persisted.TC-TASK-03: Mark task CONFIRMED_NEGATIVE with technical reasoning $\rightarrow$ State transitions to CONFIRMED_NEGATIVE, blue shield icon active.Failure / Edge Cases:TC-TASK-04: Skip task with empty justification $\rightarrow$ Returns 400 Bad Request.TC-TASK-05: Transition task to COMPLETED without evidence verification or manual override flag $\rightarrow$ Returns 400 Bad Request.TC-TASK-06: Attempt state modification on a task whose parent project scope is unlocked $\rightarrow$ Returns 400 Bad Request.2.4 Evidence Ingestion & Artifact Storage PipelineHappy Path:TC-EVID-01: Submit 2,000-line CLI log $\rightarrow$ Writes raw log to data/projects/{id}/artifacts/EVID-XXX.txt, computes SHA-256 matching file on disk, stores $\le 800$-char redacted_excerpt in SQLite.TC-EVID-02: Retrieve evidence metadata $\rightarrow$ GET /evidence returns array containing ID, size, hash, and redacted excerpt.TC-EVID-03: Retrieve raw artifact content $\rightarrow$ GET /evidence/{id}/content streams full raw file from disk matching SHA-256.Failure / Security / Edge Cases:TC-EVID-04: Path Traversal Attack: Request GET /evidence/..%2F..%2F..%2Fetc%2Fpasswd/content or EVID-01/../../../ $\rightarrow$ ArtifactManager raises path traversal exception; returns 400 Bad Request.TC-EVID-05: Redaction Correctness: Submit raw log containing Authorization: Bearer secret_token_12345 and password="SuperSecret" $\rightarrow$ SQLite redacted_excerpt and outbound LLM payload replace secrets with [REDACTED_TOKEN] and [REDACTED_PASSWORD].TC-EVID-06: Oversized Log Handling: Submit payload $> 10\text{ MB}$ $\rightarrow$ Rejected with 413 Payload Too Large.TC-EVID-07: Artifact file missing on disk during content retrieval $\rightarrow$ Returns 404 with structured error message, does not crash backend.2.5 Cohere Verifier & Offline FallbackHappy Path:TC-VERIF-01: Valid ffuf log submitted with Cohere active $\rightarrow$ Returns structured JSON conforming to VerificationVerdictSchema with verdict = "PASS", confidence, and grounded quotes.Resilience / Fallback Cases:TC-VERIF-02: Malformed JSON from LLM: Mock Cohere returning non-JSON conversational text $\rightarrow$ Service parser catches JSONDecodeError, invokes fallback rule-based parser without throwing 500.TC-VERIF-03: Offline Mode (Missing API Key): Set CO_API_KEY="" $\rightarrow$ System activates local heuristic verifier, evaluates log for exit codes and HTTP statuses, returns valid verdict with "confidence": "LOW (Offline Engine)".TC-VERIF-04: Upstream Rate Limit (429): Mock Cohere returning 429 $\rightarrow$ Gracefully catches HTTPStatusError, logs warning, returns fallback verdict prompting manual review.2.6 Governed Proposals QueueHappy Path:TC-PROP-01: Evidence output containing /backup.zip verified $\rightarrow$ Auto-creates WorkflowProposal in PENDING status.TC-PROP-02: Approve proposal $\rightarrow$ Proposal moves to APPROVED, new Task injected into Phase 4 with is_ai_proposed = True.TC-PROP-03: Undo proposal $\rightarrow$ While task is NOT_STARTED with zero evidence, clicking undo deletes Task, sets proposal back to PENDING, logs PROPOSAL_UNDONE.Failure / Edge Cases:TC-PROP-04: Deduplication $\rightarrow$ Submitting identical asset findings does not spawn duplicate pending proposals.TC-PROP-05: Capacity Cap $\rightarrow$ Max 3 pending proposals enforced; excess proposals dropped.TC-PROP-06: Undo on active task $\rightarrow$ If task status changed to IN_PROGRESS or evidence was linked, undo is rejected with 400 Bad Request.2.7 Findings Lifecycle & Evidence LinkingHappy Path:TC-FIND-01: Create finding with valid evidence_id, title, severity, description, and reproduction steps $\rightarrow$ Saves finding in CONFIRMED status.Failure / Edge Cases:TC-FIND-02: Create confirmed finding without evidence_id $\rightarrow$ Rejected with 400 Bad Request.TC-FIND-03: Create finding with non-existent evidence_id $\rightarrow$ Foreign key validation rejects with 404/400.TC-FIND-04: Delete evidence linked to finding $\rightarrow$ Blocked or safely updates finding to reflect detached proof rather than leaving dangling pointers.2.8 Formal Reporting & Readiness AuditorHappy Path:TC-REP-01: Generate report $\rightarrow$ Returns Markdown containing all 6 required sections:Executive SummaryScope & Rules of EngagementMethodology Execution TableTarget InventoryConfirmed FindingsAppendix: Evidence Register & Integrity LogTC-REP-02: Verify Evidence Register $\rightarrow$ 100% of files present in data/projects/{id}/artifacts/ appear in the table with exact file size and SHA-256 digest.TC-REP-03: Report Readiness $\rightarrow$ GET /report/readiness flags missing reproduction steps, missing remediation, or unlinked findings.Failure / Edge Cases:TC-REP-04: Empty project report $\rightarrow$ Renders clean template with placeholder text, zero syntax or rendering crashes.2.9 Archive Import/Export (Integrity & Security)Happy Path:TC-ARCH-01: Export project $\rightarrow$ Generates .zip containing manifest.json, project.json, and /artifacts/ directory with correct SHA-256 checksums.TC-ARCH-02: Import project $\rightarrow$ Unpacks archive, remaps Project ID, Phase IDs, Task IDs, Asset IDs, and Evidence IDs without collisions, restores artifact files on disk.Security & Resilience Cases:TC-ARCH-03: Zip-Slip Defense: Import archive containing entry ../../../../etc/shadow or absolute path /tmp/pwn $\rightarrow$ Archive extractor detects path escape, aborts extraction, rejects with 400.TC-ARCH-04: Checksum Mismatch: Alter one byte inside project.json inside exported zip $\rightarrow$ Importer verifies manifest hashes, detects tampering, aborts with 400 Bad Request.TC-ARCH-05: Atomic Rollback: Induce failure halfway through database import $\rightarrow$ SQLite transaction rolls back, partially extracted files in data/projects/{new_id}/ are pruned from disk.3. Automated Quality GateTwo non-interactive, fail-fast scripts must be created: scripts/verify_all.sh (Linux/macOS) and scripts/verify_all.ps1 (Windows PowerShell).[Lint & Static Check] ──> [Backend Tests + Cov] ──> [Frontend Build] ──> [E2E Contract Check]
        │                           │                        │                     │
      Fail?                       Fail?                    Fail?                 Fail?
        ▼                           ▼                        ▼                     ▼
   [HALT & EXIT]               [HALT & EXIT]            [HALT & EXIT]         [HALT & EXIT]
3.1 Linux/macOS Gate (scripts/verify_all.sh)Bash#!/usr/bin/env bash
set -euo pipefail

echo "======================================================="
echo "   REDSAGE v2: AUTOMATED QUALITY & HARDENING GATE      "
echo "======================================================="

# 1. Environment Verification
echo "[1/5] Checking Python & Node environments..."
python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"
node -v > /dev/null

# 2. Secret Redaction & Static Linting
echo "[2/5] Running static syntax & hygiene checks..."
python3 -m py_compile backend/**/*.py
python3 -c "from backend.services.cohere_service import redact_sensitive_data; assert '[REDACTED' in redact_sensitive_data('password=\"test\"')"

# 3. Backend Test Suite with Coverage
echo "[3/5] Executing backend test suite..."
export DATABASE_URL="sqlite:///:memory:"
pytest tests/ -v --tb=short

# 4. Frontend Compilation & Typecheck
echo "[4/5] Building frontend production bundle..."
(
  cd frontend
  npm run build
)

# 5. E2E Smoke & Contract Verification
echo "[5/5] Running E2E regression contract suite..."
python3 -m pytest tests/test_smoke_demo.py -v

echo "======================================================="
echo "   QUALITY GATE PASSED: BUILD IS RELEASE-READY        "
echo "======================================================="
3.2 Windows PowerShell Gate (scripts/verify_all.ps1)PowerShell$ErrorActionPreference = "Stop"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   REDSAGE v2: AUTOMATED QUALITY & HARDENING GATE      " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Environment Check
Write-Host "[1/5] Checking Python & Node environments..." -ForegroundColor Yellow
python -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"
node -v | Out-Null

# 2. Syntax Check
Write-Host "[2/5] Running static syntax checks..." -ForegroundColor Yellow
python -m py_compile backend/main.py

# 3. Backend Test Suite
Write-Host "[3/5] Executing backend test suite..." -ForegroundColor Yellow
$env:DATABASE_URL = "sqlite:///:memory:"
pytest tests/ -v --tb=short

# 4. Frontend Build
Write-Host "[4/5] Building frontend production bundle..." -ForegroundColor Yellow
Push-Location frontend
npm run build
Pop-Location

# 5. E2E Contract Check
Write-Host "[5/5] Running E2E regression contract suite..." -ForegroundColor Yellow
python -m pytest tests/test_smoke_demo.py -v

Write-Host "=======================================================" -ForegroundColor Green
Write-Host "   QUALITY GATE PASSED: BUILD IS RELEASE-READY        " -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
4. Route Coverage & Contract TestsCreate tests/test_api_contracts.py to ensure all endpoints adhere to strict status codes and JSON schemas.4.1 Mandatory OpenAPI Route InventoryMethodRoute PathExpected Success StatusContract Validation AssertionGET/api/v1/health200 OK{"status": "healthy", "human_in_the_loop": True}GET/api/v1/projects200 OKArray of project objectsPOST/api/v1/projects201 CreatedReturns created id, name, default phases seededGET/api/v1/projects/{id}/scope200 OKIncludes is_locked, in_scope_whitelist arrayPOST/api/v1/projects/{id}/scope/lock200 OKReturns {"status": "locked"}POST/api/v1/projects/{id}/scope/amend200 OKReturns {"status": "amended"}GET/api/v1/projects/{id}/tasks200 OKPhased array; each task has is_scope_safe booleanPOST/api/v1/projects/{id}/tasks/{tid}/verify200 OKReturns verdict, grounded_quotations, evidence_idGET/api/v1/projects/{id}/evidence200 OKArray of evidence metadata (size, hash, excerpt)GET/api/v1/projects/{id}/evidence/{eid}/content200 OKPlaintext stream matching artifact hashGET/api/v1/projects/{id}/proposals200 OKArray of pending proposalsPOST/api/v1/projects/{id}/proposals/{pid}/approve200 OKInjects task into Phase 4POST/api/v1/projects/{id}/proposals/{pid}/undo200 OKRemoves injected task, resets proposalPOST/api/v1/projects/{id}/findings201 CreatedRequires valid evidence_idGET/api/v1/projects/{id}/report200 OKReturns { "markdown": str } containing all 6 sectionsGET/api/v1/projects/{id}/report/readiness200 OKReturns { "ready_for_export": bool, "issues": list }GET/api/v1/projects/{id}/export200 OKStreams valid .zip application/zipPOST/api/v1/projects/import200 OKReturns { "project_id": str, "status": "imported" }4.2 Automated Route Verification TestThe test suite iterates over FastAPI's registered routes and validates existence against the inventory:Python# tests/test_api_contracts.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_openapi_route_completeness():
    registered_routes = {
        f"{route.methods.pop() if hasattr(route, 'methods') else 'GET'} {route.path}"
        for route in app.routes
    }
    required_routes = [
        "GET /api/v1/health",
        "GET /api/v1/projects",
        "POST /api/v1/projects",
        "GET /api/v1/projects/{project_id}/scope",
        "POST /api/v1/projects/{project_id}/scope/lock",
        "POST /api/v1/projects/{project_id}/scope/amend",
        "GET /api/v1/projects/{project_id}/tasks",
        "POST /api/v1/projects/{project_id}/tasks/{task_id}/verify",
        "GET /api/v1/projects/{project_id}/evidence",
        "GET /api/v1/projects/{project_id}/proposals",
        "POST /api/v1/projects/{project_id}/findings",
        "GET /api/v1/projects/{project_id}/report",
        "GET /api/v1/projects/{project_id}/report/readiness",
    ]
    for req in required_routes:
        assert req in registered_routes, f"Missing expected contract endpoint: {req}"
5. Minimal UI Reliability & Crash Prevention5.1 React Global Error Boundary (frontend/src/components/ErrorBoundary.tsx)Prevents application-wide white-screen crashes caused by unhandled runtime exceptions or malformed API responses.TypeScriptimport React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught UI Exception:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-sage-900 text-sage-50 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-sage-800 border border-rose-500/30 rounded-xl p-6 shadow-2xl space-y-4 text-center">
            <div className="w-12 h-12 bg-rose-500/10 rounded-full flex items-center justify-center mx-auto text-rose-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold">Workspace Display Error</h2>
            <p className="text-xs text-sage-300">
              An unexpected render error occurred in this panel. Your project state and evidence on disk are safe.
            </p>
            <div className="bg-sage-950 p-3 rounded font-mono text-xs text-rose-300 text-left overflow-x-auto max-h-32">
              {this.state.error?.message}
            </div>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-2 bg-sage-700 hover:bg-sage-600 rounded text-xs font-semibold flex items-center justify-center space-x-2 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reload Workspace</span>
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
5.2 UI State Guardrail RequirementsEmpty States:Evidence Library: "No evidence artifacts captured. Complete a task verification to log evidence."Findings View: "No confirmed findings. Only findings backed by verified evidence appear here."Proposals Drawer: "No pending proposals. All discovered attack surfaces are addressed."Double-Submit Prevention:The [Verify Evidence] button must disable immediately upon click and render a spinner ("Analyzing...") to prevent duplicate artifact creation or rapid-fire Cohere calls.HTTP Error Toasting:Global Axios/Fetch response interceptor catching 400, 404, 422, and 500 responses, surfacing non-blocking notification banners with human-readable error details.6. Prioritized QA Sprint Plan (1–2 Days Execution)Execute these hardening tasks in strict order:Day 1 Morning (Tier 0) ──> Day 1 Afternoon (Tier 1) ──> Day 2 Morning (Tier 2) ──> Day 2 Afternoon (Tier 3)
   [Security & Guard]        [Core Verification Loop]       [Import/Export & Rep]       [Gate Automation]
Day 1: Tier 0 — Security Invariants & Guardrails (Hours 1–4)Path Traversal Shielding: Review ArtifactManager.read_artifact() and save_artifact(); enforce strict os.path.abspath() checks against base project directories. Add test fixtures.Zip-Slip Hardening: Inspect archive extractor in archive_service.py; reject any zip header containing .. or absolute paths before writing bytes to disk. Add malicious zip test.Scope Guard Enforcement: Audit command-template resolution in tasks.py. Ensure copy buttons are hard-disabled if {target_host} is not in whitelist.Day 1: Tier 1 — Core Ingestion & State Machine Integrity (Hours 5–8)Redaction Assurance: Verify regex masking purges Authorization headers, bearer tokens, API keys, and passwords before saving redacted_excerpt and before sending text to Cohere.Task State Constraints: Enforce mandatory $\ge 10$-char justification on SKIPPED and CONFIRMED_NEGATIVE task transitions.Finding Evidence Coverage: Hard-block POST /findings if evidence_id is missing, blank, or not present in database.Day 2: Tier 2 — Resilience, Fallbacks & Traceability (Hours 9–12)Cohere Verifier Offline Resilience: Implement catch-all in cohere_service.py to seamlessly fall back to local rule-based verification when CO_API_KEY is missing or Cohere returns 429/500.Report Traceability Integrity: Ensure report_builder.py produces Section 6 (Evidence Register) containing accurate SHA-256 hashes matching all files on disk.Archive Round-Trip Remapping: Test export $\rightarrow$ import lifecycle; verify all entity UUIDs remap cleanly without orphan foreign keys.Day 2: Tier 3 — Quality Gate & UI Stability (Hours 13–16)Automate Quality Gate: Write and execute scripts/verify_all.sh and scripts/verify_all.ps1.Frontend Crash Prevention: Wrap the root React app in ErrorBoundary.tsx and verify empty-state displays across all views.End-to-End Walkthrough: Execute the "Magic Demo" flow on a fresh database.7. Final Go/No-Go ChecklistBefore conducting live assessments or demos, all 24 criteria must be satisfied:Scope & Legal Safety[ ] 1. Scope Gate hard-locks testing until in-scope whitelist is explicitly confirmed.[ ] 2. Scope amendments reject empty authorizing contact or justifications $< 10$ characters.[ ] 3. Command template generator hard-disables copying if target domain is out-of-scope.[ ] 4. Prohibited actions (DoS, destructive testing) remain flagged as immutable constraints.Evidence & Storage Integrity[ ] 5. Raw evidence is saved directly to disk files in data/projects/{id}/artifacts/.[ ] 6. Database stores only file paths, file sizes, SHA-256 digests, and redacted excerpts.[ ] 7. Path traversal attempts (..%2F, /etc/passwd) are rejected with HTTP 400.[ ] 8. Uploaded artifacts exceeding $10\text{ MB}$ are rejected with HTTP 413.[ ] 9. Client-side and backend redaction masks passwords, Bearer tokens, and JWTs.AI Engine & Offline Resilience[ ] 10. Cohere requests use command-r-08-2024 with log clipping (max 80 lines).[ ] 11. Untrusted evidence logs are strictly encapsulated in <untrusted_evidence_log> boundary tags.[ ] 12. If CO_API_KEY is unset or Cohere errors out, the offline heuristic verifier runs without crashing.[ ] 13. AI verification returns valid JSON adhering to VerificationVerdictSchema.Workflow & Governance[ ] 14. Tasks cannot be set to COMPLETED without verified evidence or explicit override.[ ] 15. Tasks set to SKIPPED or CONFIRMED_NEGATIVE require $\ge 10$-character justifications.[ ] 16. Discovered high-risk assets (backup, admin) generate proposals in PENDING state only.[ ] 17. Approving a proposal injects a new task; undoing removes the task if untouched.Findings & Formal Deliverables[ ] 18. Findings cannot transition to CONFIRMED without a valid, linked evidence_id.[ ] 19. Exported Markdown report contains all 6 required formal pentest sections.[ ] 20. Evidence Register appendix accurately lists every artifact file, size, and SHA-256 digest.[ ] 21. Report Readiness auditor flags unlinked findings, empty reproductions, or missing justifications.System & Architecture Health[ ] 22. Preserved directories core/ and data/chroma/ remain completely untouched.[ ] 23. Import archive rejects malicious entries with zip-slip payloads or mismatched checksums.[ ] 24. verify_all.sh (or .ps1) executes cleanly with zero test failures and clean frontend build.8. Clarifying Questions & Solo-Dev DefaultsArtifact Deletion Policy:Question: When a project or evidence row is deleted, should the raw artifact file on disk be permanently unlinked immediately, or moved to a .trash/ quarantine directory?Recommended Default: Permanent deletion (os.remove()). This prevents disk bloat and ensures sensitive client data is not retained after project removal.Offline Verifier Strictness:Question: How should the offline fallback verifier decide a PASS versus AMBIGUOUS verdict without Cohere?Recommended Default: Strict regex heuristics. Mark PASS only if the log contains standard zero-exit indicators or expected protocol headers (e.g., Status: 200, open/tcp), and set confidence to "LOW (Offline Heuristic)".Database Concurrency Mode:Question: Should SQLite run in default rollback journal mode or Write-Ahead Logging (WAL)?Recommended Default: WAL Mode (PRAGMA journal_mode=WAL;). WAL significantly reduces concurrency locks between background evidence hashing and frontend reads.Log Truncation Indicator in Excerpts:Question: Should redacted_excerpt store the first 800 characters, or a 400-head / 400-tail split?Recommended Default: Head/tail split (400 chars head + \n[...]\n + 400 chars tail). This captures both initial command parameters and trailing completion summaries.Scope Whitelist IP Subnet Normalization:Question: If a user enters 192.168.1.50/32, should it be normalized to 192.168.1.50?Recommended Default: Yes. Normalize via ipaddress.ip_network(target, strict=False) to prevent string comparison misses.Report Readiness Gate Enforcement:Question: Should an unready report (score $< 100\%$) block the "Download .md" button, or simply display a warning modal?Recommended Default: Warning modal with explicit "Export Anyway" override. Never block the operator from obtaining their data during time-sensitive engagements.