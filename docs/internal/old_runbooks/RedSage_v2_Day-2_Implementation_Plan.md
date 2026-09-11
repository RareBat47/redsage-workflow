RedSage v2: Day-2 Implementation Plan
Professional Evidence Artifacts, Traceability Engine, and Formal Pentest Reporting

1. Day-2 Scope: MUST / NICE / NOT TODAY (8–12 Hour Timebox)
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAY-2 CORE UPGRADE LOOP                           │
│                                                                             │
│  [Task Evidence Paste] ──> [Disk Artifact Storage] + [DB Metadata Excerpt]  │
│                                      │                                      │
│  [Formal Report + Evidence Index] ◄──┴──> [Evidence Library Screen]         │
└─────────────────────────────────────────────────────────────────────────────┘
MUST Build (Critical Path for Day-2)
Disk-Based Artifact Storage (data/projects/{project_id}/artifacts/):

Persist raw tool outputs to .txt/.log files on disk with SHA-256 integrity verification.

Path traversal protection ensuring all file operations remain inside the project's sandbox.

Database Schema Evolution (backend/models/schema.py):

Update Evidence table: remove full raw_content, add file_path, file_size_bytes, and redacted_excerpt (first 500–1000 chars, regex-redacted).

Migration script (backend/migrate_day2.py) to safely transition existing SQLite databases without data loss.

Evidence Retrieval API:

GET /api/v1/projects/{id}/evidence: List all evidence items with metadata and excerpts.

GET /api/v1/projects/{id}/evidence/{evidence_id}/content: Read raw artifact content on demand (with size limits).

Evidence Library View (Frontend):

Filterable grid/list showing: Evidence ID, Source Task, Asset, File Size, SHA-256 hash, and a collapsible Excerpt preview.

Drawer/Modal to view the full raw artifact loaded on demand.

Formal Pentest Reporting with Evidence Traceability:

Unique short identifiers for evidence (EVID-001, EVID-002).

Findings explicitly cite [Evidence Ref: EVID-XXX].

Dynamic Appendix: Evidence Register & Integrity Log generated at the end of the report (Table: ID, Source Task, File Name, SHA-256, Timestamp).

NICE to Have (If Time Permits in Hours 10–12)
Filter Evidence Library by task type or finding linkage.

Client-side copy button for SHA-256 hashes.

One-click "Jump to Task" from the Evidence Library.

NOT Today (Strictly Deferred to Future Sprints)
Image/screenshot file uploads (plain-text and log artifacts only for Day-2).

Automated remote storage (S3/MinIO) or cloud syncing.

PDF binary compilation (report output remains structured GitHub-Flavored Markdown).

Automated retesting or active tool execution.

2. Architecture & Storage Migration Strategy
2.1 Filesystem Directory Layout
Plaintext
data/
├── methodologies/
│   └── baseline_methodology.json
├── projects/
│   └── {project_id}/
│       └── artifacts/
│           ├── EVID-001_1725801200.txt
│           └── EVID-002_1725801550.txt
└── redsage.db
2.2 Security & Path-Traversal Defense
All artifact read/write operations must resolve against an absolute project directory path:

Python
import os
from fastapi import HTTPException

def get_safe_artifact_path(project_id: str, filename: str) -> str:
    base_dir = os.path.abspath(f"data/projects/{project_id}/artifacts")
    target_path = os.path.abspath(os.path.join(base_dir, filename))
    if not target_path.startswith(base_dir):
        raise HTTPException(status_code=400, detail="Invalid artifact path: Directory traversal detected")
    return target_path
3. Data Model Updates & API Contracts
3.1 SQLAlchemy Schema Updates (backend/models/schema.py)
Python
class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True)            # e.g., "EVID-001" or UUID
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    evidence_type = Column(String, nullable=False, default="TERMINAL_LOG")
    file_path = Column(String, nullable=False)        # Relative disk path: "data/projects/.../artifacts/..."
    file_size_bytes = Column(Integer, nullable=False, default=0)
    sha256_hash = Column(String(64), nullable=False)
    redacted_excerpt = Column(Text, nullable=False)   # First 800 chars, regex-redacted, for UI previews
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="evidence")
    task = relationship("Task", back_populates="evidence")
3.2 Database Migration Script (backend/migrate_day2.py)
This script checks existing SQLite columns, writes existing raw_content to disk files, updates the schema, and populates file_path and redacted_excerpt.

Python
import os
import sqlite3
import hashlib

DB_PATH = "data/redsage.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("No existing database to migrate.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check columns in evidence table
    cursor.execute("PRAGMA table_info(evidence)")
    columns = [row[1] for row in cursor.fetchall()]

    if "file_path" not in columns:
        print("Migrating evidence table to filesystem-backed storage...")
        cursor.execute("ALTER TABLE evidence ADD COLUMN file_path TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE evidence ADD COLUMN file_size_bytes INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE evidence ADD COLUMN redacted_excerpt TEXT DEFAULT ''")

        # Migrate existing rows
        cursor.execute("SELECT id, project_id, raw_content FROM evidence")
        rows = cursor.fetchall()
        for evid_id, project_id, raw_content in rows:
            artifacts_dir = f"data/projects/{project_id}/artifacts"
            os.makedirs(artifacts_dir, exist_ok=True)
            filename = f"{evid_id}.txt"
            full_path = os.path.join(artifacts_dir, filename)

            raw_bytes = (raw_content or "").encode("utf-8")
            with open(full_path, "wb") as f:
                f.write(raw_bytes)

            sha256 = hashlib.sha256(raw_bytes).hexdigest()
            excerpt = (raw_content or "")[:800]

            cursor.execute(
                "UPDATE evidence SET file_path = ?, file_size_bytes = ?, sha256_hash = ?, redacted_excerpt = ? WHERE id = ?",
                (full_path, len(raw_bytes), sha256, excerpt, evid_id)
            )

        conn.commit()
        print(f"Successfully migrated {len(rows)} evidence records to disk artifacts.")
    else:
        print("Evidence table already up-to-date.")

    conn.close()

if __name__ == "__main__":
    migrate()
4. Formal Pentest Reporting Engine Specification
The report engine must generate an audit-ready, 6-section report with full traceability.

4.1 Required Report Sections
Executive Summary & Posture Overview

Scope & Rules of Engagement Attestation (locked whitelist, rate limit, excluded targets)

Assessment Methodology & Task Audit Matrix (Phase, Task Title, Status, Completed Timestamp)

Target Asset Inventory (Discovered hosts, open ports, web endpoints)

Detailed Technical Findings (Mapped to CWE, Severity, Affected Asset, Reproduction Steps, Evidence Citation)

Appendix: Evidence Register & Integrity Log (Complete audit table of all artifacts)

4.2 Evidence Register Schema (Appendix Table)
Every generated report must append this table:

Markdown
## Appendix: Evidence Register & Integrity Log

| Evidence ID | Source Task | Artifact File | File Size | SHA-256 Digest | Timestamp (UTC) |
|---|---|---|---|---|---|
| `EVID-001` | 2.2 Content Discovery | `EVID-001_1725801200.txt` | 1,420 B | `a3f8e9...` | 2026-09-08 10:15:00 |
| `EVID-002` | 4.1 Headers Audit | `EVID-002_1725801550.txt` | 840 B | `9b2c11...` | 2026-09-08 10:22:15 |
5. UI / Screen Specifications
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UPDATED TOP NAVIGATION                            │
│  [RedSage v2]  Project: [Acme Corp ▼]  [Roadmap] [Evidence Library] [Report]│
└─────────────────────────────────────────────────────────────────────────────┘
5.1 Evidence Library View (frontend/src/pages/EvidenceLibrary.tsx)
Header: Total evidence count, total disk footprint (e.g., 4 Artifacts (38.2 KB)), and quick search input.

Artifact Cards / Table:

Columns: Evidence ID chip (EVID-001), Linked Task name, File Size, Timestamp, SHA-256 (truncated with copy button).

Collapsible Preview: Displays redacted_excerpt instantly.

Primary Action: [View Full Artifact] button.

Artifact Viewer Drawer:

Slide-over panel that fetches the complete raw text on demand via GET /api/v1/projects/{id}/evidence/{evidence_id}/content.

Monospaced code block with syntax styling and a [Copy Raw Log] button.

5.2 Task Workspace Updates
Evidence Tray displays the newly minted Evidence ID upon successful verification (e.g., ✔ Saved as Artifact EVID-003).

Direct link chip: [View in Evidence Library].

5.3 Findings View Updates
When creating/editing a finding, the "Linked Evidence" dropdown displays:

[EVID-001] Task 2.2: Web Content Discovery (1.4 KB | a3f8e9...)

6. Step-by-Step Day-2 Milestones (Agent Tickets)
Milestone 1: Filesystem Artifact Engine & Database Migration
Files to create/edit:

backend/services/artifact_manager.py

backend/models/schema.py

backend/migrate_day2.py

Implementation:

Build ArtifactManager with save_artifact(), read_artifact(), and path traversal validation.

Update Evidence model to include file_path, file_size_bytes, redacted_excerpt.

Run python -m backend.migrate_day2.

Done When: Existing and new evidence items write raw logs to data/projects/{id}/artifacts/ and store clean excerpts in SQLite.

Test:

Bash
python -c "from backend.services.artifact_manager import save_artifact; p = save_artifact('test-proj', 'EVID-TEST', 'sample output'); print('Saved:', p)"
Milestone 2: Evidence API Endpoints
Files to create/edit:

backend/routers/evidence.py

Implementation:

Update POST /api/v1/projects/{id}/tasks/{task_id}/verify to write files via ArtifactManager.

Add GET /api/v1/projects/{id}/evidence: Returns list of evidence metadata + excerpts.

Add GET /api/v1/projects/{id}/evidence/{evidence_id}/content: Returns full raw artifact text (capped at 5 MB safety limit).

Done When: FastAPI returns evidence lists and streams full artifact text.

Test:

Bash
curl -s http://127.0.0.1:8000/api/v1/projects/{project_id}/evidence | grep "EVID-"
Milestone 3: Evidence Library Screen (Frontend)
Files to create/edit:

frontend/src/pages/EvidenceLibrary.tsx

frontend/src/components/EvidenceModal.tsx

frontend/src/services/api.ts

frontend/src/App.tsx (Add navigation tab: Roadmap | Evidence Library | Report Studio)

Done When: User can click "Evidence Library", browse all stored artifacts, copy SHA-256 hashes, and open full raw logs in a slide-over modal.

Test: Verify in browser at [http://127.0.0.1:5173](http://127.0.0.1:5173).

Milestone 4: Traceable Formal Report Builder
Files to create/edit:

backend/services/report_builder.py

backend/routers/reports.py

Implementation:

Enhance report_builder.py to compile:

Executive Summary

Scope & Rules of Engagement Attestation

Methodology Execution Table

Target Inventory

Confirmed Findings (with explicit Evidence ID: EVID-XXX citations)

Appendix: Evidence Register & Integrity Log (listing file path, size, SHA-256, date)

Done When: GET /api/v1/projects/{id}/report returns complete Markdown with the Evidence Register table populated.

Test:

Bash
curl -s http://127.0.0.1:8000/api/v1/projects/{project_id}/report | grep "Appendix: Evidence Register"
Milestone 5: Automated Testing Suite
Files to create/edit:

tests/test_artifacts.py

tests/test_report_traceability.py

Implementation:

Unit test for path traversal rejection.

Unit test verifying evidence SHA-256 matches disk file contents.

Integration test verifying that every confirmed finding in a report has a matching entry in the Evidence Register table.

Done When: pytest tests/ runs with 100% green passing tests.

7. Definition of Done Checklist (Day-2)
[ ] 1. SQLite database successfully migrated without data loss (backend/migrate_day2.py).

[ ] 2. Raw tool outputs are stored as plain-text files under data/projects/{id}/artifacts/.

[ ] 3. Path traversal attempts (e.g., ../../etc/passwd) are rejected with HTTP 400.

[ ] 4. Database evidence table stores only file_path, file_size_bytes, sha256_hash, and redacted_excerpt.

[ ] 5. Redacted excerpts in DB never contain plaintext passwords, Bearer tokens, or JWTs.

[ ] 6. GET /api/v1/projects/{id}/evidence returns all project artifacts with metadata.

[ ] 7. GET /api/v1/projects/{id}/evidence/{evidence_id}/content loads full raw log text on demand.

[ ] 8. Frontend includes a dedicated Evidence Library tab in the main navigation.

[ ] 9. Evidence Library displays artifact ID, linked task, timestamp, size, and SHA-256.

[ ] 10. Clicking an artifact opens a viewer displaying the full raw tool output with a Copy button.

[ ] 11. Creating a finding links to a specific Evidence ID (EVID-XXX).

[ ] 12. Report Studio renders the Evidence Register & Integrity Log appendix table.

[ ] 13. Every confirmed finding in the report explicitly references its supporting Evidence ID.

[ ] 14. Exported .md report contains all 6 required formal pentest sections.

[ ] 15. Preserved core/ directory remains completely untouched.

[ ] 16. Automated test suite (pytest tests/) passes with 100% green tests.

8. The Kilo Code Prompt (Single Paste for Day-2 Execution)
Copy and paste the prompt below into your VS Code coding agent to run the entire Day-2 build autonomously:

Markdown
You are an elite software architect and full-stack engineer upgrading "RedSage v2" for Day-2: Evidence Artifacts, Integrity Auditing, and Formal Pentest Reporting.

OBJECTIVE:
Transform RedSage v2 from storing raw evidence in SQLite to storing raw evidence as disk artifacts in `data/projects/{project_id}/artifacts/`, store only metadata and redacted excerpts in the database, implement the Evidence Library screen, and generate audit-grade Markdown reports with a formal Evidence Register appendix.

CRITICAL RULES (NON-NEGOTIABLE):
1. PRESERVE `core/`: DO NOT modify, delete, or touch any files in `core/` (config.py, embeddings.py, kb_engine.py) or `data/chroma/`.
2. HUMAN-IN-THE-LOOP: Never run security tools or network scans directly.
3. NO EXPLOIT PAYLOADS: Keep all command suggestions strictly high-level and safe (recon/auditing).
4. UNTRUSTED DATA & REDACTION: Always clip logs (max 80 lines) and regex-redact secrets (tokens, passwords, JWTs) before sending to Cohere.
5. PATH SAFETY: Strictly prevent directory traversal when saving or reading artifacts from disk.
6. UPDATE PROGRESS.md: Maintain and update `PROGRESS.md` after completing each milestone.

EXECUTE THESE MILESTONES IN SEQUENCE:

### Milestone 1: Filesystem Artifact Engine & DB Migration
1. Create `backend/services/artifact_manager.py`:
   - `save_artifact(project_id: str, evidence_id: str, raw_content: str) -> tuple[str, int, str]` (returns file_path, file_size_bytes, sha256_hash).
   - `read_artifact(project_id: str, filename: str) -> str` (validates path stays within project artifacts directory).
2. Update `Evidence` in `backend/models/schema.py`:
   - Add `file_path = Column(String, nullable=False)`
   - Add `file_size_bytes = Column(Integer, nullable=False, default=0)`
   - Add `redacted_excerpt = Column(Text, nullable=False)`
   - Remove or deprecate `raw_content` column from DB schema.
3. Create `backend/migrate_day2.py`:
   - Script that alters existing `data/redsage.db` to add the new columns, exports any existing `raw_content` to `data/projects/{project_id}/artifacts/`, and computes SHA-256 and excerpts.
   - Run `python backend/migrate_day2.py` to execute the migration.

### Milestone 2: Evidence API Endpoints & Verification Update
1. Update `backend/routers/evidence.py`:
   - In `POST /tasks/{task_id}/verify`:
     - Assign human-friendly Evidence ID (e.g. `EVID-001` based on count or short UUID).
     - Save raw content to disk using `ArtifactManager`.
     - Save metadata, SHA-256, and `redacted_excerpt` (first 800 chars, regex-redacted) into SQLite.
     - Clip and redact in memory, then call Cohere `command-r-08-2024` for verification.
   - Add `GET /api/v1/projects/{project_id}/evidence`: Return list of evidence metadata, excerpts, and task titles.
   - Add `GET /api/v1/projects/{project_id}/evidence/{evidence_id}/content`: Read raw artifact from disk and return `{ "content": text }`.

### Milestone 3: Evidence Library Frontend Screen
1. In `frontend/src/types/index.ts`, add `EvidenceItem` interface.
2. In `frontend/src/services/api.ts`, add calls for `getProjectEvidence()` and `getEvidenceContent()`.
3. Create `frontend/src/components/EvidenceModal.tsx`:
   - Slide-over or modal viewer to display full raw artifact text with line numbers and a [Copy Content] button.
4. Create `frontend/src/pages/EvidenceLibrary.tsx`:
   - Table/grid listing all project evidence: ID chip, Source Task name, File Size, SHA-256 hash (with copy icon), Timestamp, and Excerpt preview.
   - [View Full Artifact] button that opens `EvidenceModal`.
5. Update `frontend/src/App.tsx` and `Header.tsx` to include top navigation switching between:
   - [Roadmap Canvas]
   - [Evidence Library]
   - [Report Studio]

### Milestone 4: Traceable Formal Report Builder
1. Update `backend/services/report_builder.py` to produce a professional 6-section pentest report:
   - Section 1: Executive Summary & Posture Overview
   - Section 2: Scope & Rules of Engagement Attestation
   - Section 3: Assessment Methodology & Task Execution Matrix
   - Section 4: Target Asset Inventory
   - Section 5: Confirmed Findings (each explicitly referencing its Evidence ID, CWE, CVSS, and Reproduction steps)
   - Section 6: Appendix: Evidence Register & Integrity Log (table mapping Evidence ID, Source Task, File Name, Size, SHA-256, and Date).
2. Verify `GET /api/v1/projects/{project_id}/report` and `GET /api/v1/projects/{project_id}/report/download` reflect these updates.

### Milestone 5: Automated Testing & Verification
1. Create `tests/test_artifacts.py`:
   - Test `ArtifactManager` directory traversal rejection.
   - Test artifact writing and SHA-256 calculation.
2. Create `tests/test_report_traceability.py`:
   - Test that generated reports include the Evidence Register appendix.
3. Run `pytest tests/` and ensure all tests pass.
4. Verify `npm run build` in `frontend/` succeeds without errors.
5. Provide a summary of completed Day-2 deliverables and instructions for testing.

Begin Milestone 1 now. Proceed autonomously through each milestone, updating PROGRESS.md as you work.