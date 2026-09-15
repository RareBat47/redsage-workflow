# RedSage v2 → v3 Feature and Logical Implementation Map

**Status:** Living migration register
**Created:** 2026-09-13
**Source of truth:** Direct inspection of `D:\HIGH LEVELS OF WORKS\RedSage_v2`, primarily `EXPLANATION.md`, `START_HERE.md`, source files, route inventory, and tests. Code wins over documentation when they disagree.

## Purpose

RedSage v3 must absorb the useful logical implementation of v2 without blindly copying its structure or known defects. This document records every verified v2 capability, its intended v3 destination, migration state, and decisions/risks. It must be updated in the same change whenever a v2 capability is migrated, redesigned, deferred, or deliberately rejected.

## Migration states

- **Present:** implemented and verified in v3.
- **Port next:** required logical capability not yet present in v3.
- **Redesign:** capability is retained but its v3 architecture/contract must change.
- **Preserve:** retained as an isolated compatibility/data foundation.
- **Decision required:** product or security decision needed before implementation.
- **Reject:** intentionally not carried forward; rationale required.

## Current verified v3 baseline

The v3 folder currently contains only the decoupled knowledge-base subsystem:

- `core/config.py` — KB settings and environment configuration.
- `core/embeddings.py` — deterministic local embedder and optional Cohere embedder.
- `core/kb_engine.py` — ChromaDB/SQLite retrieval, lexical reranking, metadata boosts, citations, grounded answer helper.
- `interfaces/api.py` — legacy KB HTTP API (`/api/health`, `/api/ask`, `/api/kb/sources`, `/api/kb/stats`).
- `interfaces/mcp_server.py` — read-only MCP tools (`kb_search`, `kb_sources`, `kb_stats`).
- `data/chroma/` and `data/redsage.db` — preserved KB data copy.

The v2 workflow product (`backend/`, `frontend/`, workflow tables, artifact directories, and tests) is **not yet present in v3**.

## Feature mapping

| ID | Verified v2 feature / logical behavior | v2 implementation surface | v3 destination/status | Notes and acceptance direction |
|---|---|---|---|---|
| F-01 | Local-first, single-operator, human-in-the-loop operating model | `START_HERE.md`; `backend/` | **Redesign — Port next** | v3 must make custody, approvals, policy, and audit first-class rather than merely inheriting a local UI. |
| F-02 | No execution of commands, scans, sockets, or attacks | route/service behavior; safety tests | **Redesign — Port next** | Preserve as a hard invariant. Agent tools may propose and inspect; they must not become autonomous authority. |
| F-03 | Project creation/list/get and project lifecycle | `routers/projects.py`; `models/schema.py` | **Port next** | v3 domain/project model; tenant/customer boundaries must be explicit before subscription work. |
| F-04 | Project Brief, trimmed and editable | `projects.py`; `ProjectBriefPanel.tsx` | **Port next** | Brief becomes governed input to planning; retain bounded/untrusted treatment. |
| F-05 | Scope whitelist/blacklist and rate limit | `scope_validator.py`; `routers/scope.py` | **Redesign — Port next** | Preserve deny-by-default and project binding; v3 needs policy versioning and approval ownership. |
| F-06 | Scope lock and audited scope amendments | `scope.py`; `scope_amendments`; audit events | **Redesign — Port next** | Retain lock gate; add immutable decision/evidence trail and explicit approver identity. |
| F-07 | Scope gates target selection and evidence verification | `scope_validator.py`, task/evidence routes | **Port next** | Must remain enforced server-side, not only in UI. |
| F-08 | Seven-phase baseline methodology | `data/methodologies/baseline_methodology.json` | **Redesign — Port next** | Preserve as an initial methodology/versioned seed; avoid hard-coding phase assumptions into services. |
| F-09 | Baseline seeding: 7 phases × 2 tasks = 14 tasks | `workflow_engine.py`; methodology JSON | **Port next** | Seed through versioned domain migrations, not one-off implicit behavior. |
| F-10 | Display-only command templates and target substitution | task schemas/routes/frontend | **Redesign — Port next** | Keep inert previews only; policy engine must reject unsafe content and execution paths. |
| F-11 | Task state machine: NOT_STARTED, IN_PROGRESS, COMPLETED, SKIPPED, CONFIRMED_NEGATIVE | `services/task_state.py` | **Port next** | Preserve transitions and justification rules; model approvals and actor/time metadata in v3. |
| F-12 | Task ordering, priorities, archived workflow rows | `schema.py`, workflow engine | **Redesign — Port next** | Preserve traceability; archive rather than delete. |
| F-13 | Task Steps/subtasks with objective, rationale, criteria, evidence type | `task_steps` model/routes; `TaskStepsPanel.tsx` | **Port next** | Core v3 work-unit model; likely generalize to bounded agent workflow steps. |
| F-14 | Step state machine and Step→Task completion rollup | `task_state.py`; Step routes | **Port next** | Preserve one source of truth and active-step guards. |
| F-15 | Evidence capture from pasted operator output | `evidence.py`; artifact manager | **Redesign — Port next** | Preserve paste-only custody; v3 should add provenance, actor, source, and retention policy. |
| F-16 | Atomic artifact writes, size cap, SHA-256 integrity | `artifact_manager.py` | **Port next** | Preserve atomicity and hash register; resolve v2's misleading 5 MB error text. |
| F-17 | Evidence metadata and redacted excerpts; raw artifact not stored in DB | `schema.py`; artifact manager | **Port next** | Preserve separation; make sensitive-data handling policy/config explicit. |
| F-18 | Secret redaction, URL-decoding, 80-line clipping before provider calls | `cohere_service.py` | **Redesign — Port next** | Keep as mandatory egress boundary; expand tests and provider-independent implementation. |
| F-19 | Evidence verdicts PASS/FAIL/AMBIGUOUS/CONFIRMED_NEGATIVE | `VerificationVerdict`; evidence service | **Redesign — Port next** | Preserve taxonomy; require provenance and approval semantics for consequential conclusions. |
| F-20 | Offline deterministic verifier and provider-failure fallback | `cohere_service.py` | **Port next** | No-key/failure path must never auto-complete work or return provider errors as 500. |
| F-21 | Grounded quotations and extracted assets from evidence | verifier + assets routes | **Port next** | Preserve citations and extraction; bind every derived object to source evidence/hash. |
| F-22 | Asset inventory and project-scoped deduplication | `assets.py`; `assets` model | **Port next** | Retain project/value identity; fix historical/archived-title dedup ambiguity. |
| F-23 | Keyword-triggered investigation proposals | `evidence.py` | **Redesign — Port next** | Retain as a policy-controlled suggestion, never automatic execution. |
| F-24 | AI Refiner chooses canonical proposal phase with Phase 4 fallback | `asset_proposal_service.py` | **Redesign — Port next** | Replace fixed fallback assumptions with methodology/policy selection. |
| F-25 | Asset-driven task suggestions, pending cap, deduplication | `assets.py`; proposals model | **Port next** | Preserve cap and exact approval semantics; improve dedup model deliberately. |
| F-26 | Human proposal lifecycle: pending/approve/dismiss/undo | `proposals.py`; audit | **Redesign — Port next** | Core human gate. v3 must record actor, policy decision, and immutable audit receipt. |
| F-27 | Planner clarification gate before live/offline generation | `planner_service.py`; workflow routes | **Port next** | Preserve deterministic completeness gate; make required dimensions methodology/policy-configurable. |
| F-28 | Planner draft schema, canonical phase validation, Replace/Merge/Discard | planner/workflow engine | **Redesign — Port next** | Preserve transactional apply and archive-in-place; add explicit plan version and approval record. |
| F-29 | AI safety filtering and inert untrusted prompt boundaries | planner, mentor, verifier prompts/schemas | **Redesign — Port next** | Elevate to centralized policy/egress layer; test prompt injection and schema failures. |
| F-30 | Mentor modes: teach, guide, verify, summarize | `mentor_service.py`; `MentorPanel.tsx` | **Redesign — Port next** | Retain bounded assistance; never allow mentor output to mutate security state directly. |
| F-31 | Task/Step/project-scoped mentor conversations persisted | `mentor_messages`; mentor routers | **Port next** | Preserve scope isolation and redacted/clipped persistence; add customer/actor tenancy. |
| F-32 | Mentor context pack from DB metadata only, 8,000-char cap | `mentor_service.py` | **Port next** | Preserve raw-artifact exclusion and bounded context. |
| F-33 | Boss Brain read-only phase digest and project mentor | `workflow_digest.py`; `BossBrainPanel.tsx` | **Redesign — Port next** | Retain as decision-support view; derive from shared domain read models. |
| F-34 | Findings DRAFT→CONFIRMED lifecycle with evidence gate | `findings.py`; findings model | **Redesign — Port next** | Preserve evidence requirement; fix v2 evidence re-pointing behavior and add explicit confirmation actor. |
| F-35 | Audit events for state, evidence, findings, proposals, workflow, mentor | `audit_service.py`; `audit_events` | **Redesign — Port next** | v3 audit trail is a primary domain capability, immutable and exportable. |
| F-36 | Report Markdown preview/download and readiness score | `report_builder.py`, `reports.py`; report UI | **Redesign — Port next** | Preserve evidence register and readiness; resolve archived-task inconsistency before porting. |
| F-37 | Report scope attestation, methodology matrix, assets, findings, evidence register | `report_builder.py` | **Port next** | Preserve traceability fields: filename, size, SHA-256, timestamp, source links. |
| F-38 | Readiness coverage and issue calculation | `readiness_service.py` | **Port next** | Preserve shared coverage helper; make policy thresholds explicit and versioned. |
| F-39 | ZIP export with manifest/checksums and no secrets | `archives.py`; archive service | **Redesign — Port next** | Preserve portable evidence package; add customer/data-retention policy and encryption decision. |
| F-40 | ZIP import with zip-slip/expansion defenses, ID remapping, rollback | archive service/routes | **Port next** | Preserve hardening and transactional rollback; verify all remapped references. |
| F-41 | React/Vite roadmap, evidence, assets, report, Boss Brain UI | `frontend/src` | **Redesign — Port next** | v3 UI should reflect domain boundaries and approval states, not copy the single App structure. |
| F-42 | Search across findings, evidence, assets; Ctrl-K UI | search router/modal/library | **Port next** | Preserve project-scoped search; determine local index vs database query strategy. |
| F-43 | Static frontend hosting and local dev/prod-like run modes | `static_frontend.py`; scripts | **Redesign — Port next** | Preserve local-first deployment; add secure authenticated customer/organization deployment mode. |
| F-44 | FastAPI `/api/v1` application surface and 42 operations/15 routers | `backend/main.py`, routers | **Redesign — Port next** | Do not copy route count as architecture; define v3 bounded domain/API contracts. |
| F-45 | Auxiliary KB retrieval: ChromaDB + SQLite, lexical rerank and metadata boosts | v2 `core/`, v3 `core/` | **Present foundation — Redesign as governed KB** | Already ported into v3. Keep preserved data read-only while adding versioning, provenance, evaluation, and bounded consumers. |
| F-46 | Deterministic and optional Cohere embedding providers | `core/embeddings.py` | **Present foundation — Redesign provider isolation** | Already present in v3; preserve deterministic compatibility and isolate every embedding profile/collection. |
| F-47 | KB HTTP API | v2 `interfaces/api.py`; v3 same | **Present compatibility — Redesign boundary** | Existing read-only surface; place it behind the v3 KB contract and resolve the port collision before app integration. |
| F-48 | KB MCP tools for external agents | v2/v3 `interfaces/mcp_server.py` | **Present compatibility — Redesign as bounded tools** | Existing read-only tools; v3 MCP must expose governed capabilities and never unrestricted authority. |
| F-49 | Configuration via environment and local SQLite defaults | `core/config.py`, v2 backend config | **Redesign — Port next** | Preserve local defaults; separate secrets, customer config, and policy configuration. |
| F-50 | Offline operation and deterministic no-key behavior across AI surfaces | v2 AI services/tests | **Port next** | Product acceptance criterion for every v3 AI feature. |
| F-51 | Safety/security documentation and project onboarding context | `START_HERE.md`, `EXPLANATION.md`, `docs/SECURITY.md`, `AGENTS.md`, `SOUL.md` | **Port next** | v3 needs maintained ground-truth docs, change register, threat model, and agent rules. |
| F-52 | Automated unit/API/E2E tests and compile/build gates | `tests/`, `pytest.ini`, frontend build | **Port next** | Port behavior tests first; isolate test DB/artifacts; keep E2E opt-in and explain skips. |

## KB architectural decision

**Decision:** Yes—design the KB as a first-class RedSage v3 subsystem, but do not rebuild or mutate the preserved v2 KB before the v3 domain boundaries are defined.

### What v3 should preserve

- The existing ChromaDB collections and SQLite metadata as a read-only compatibility/data foundation.
- The exact deterministic embedder required to query the active local collection.
- Optional semantic embeddings in separate, explicitly identified collections.
- Lexical reranking, metadata boosts, source/trust metadata, citations, and grounded retrieval.
- Read-only HTTP/MCP access during the transition.

### What v3 should add or redesign

1. **KB as a governed domain**, not merely a `KBEngine` utility: sources, documents, chunks, versions, provenance, trust, ingestion status, and embedding profile must be explicit.
2. **Separate knowledge from customer evidence:** public/reference security knowledge, organization-owned methodology, and project evidence must have distinct custody, permissions, retention, and export rules. Evidence must never silently become shared KB content.
3. **Versioned ingestion:** immutable source/document versions, content hashes, chunking metadata, parser version, embedding model/profile, and reproducible re-indexing.
4. **Retrieval contracts:** return citations with source identity, version, chunk identity, score components, trust, and retrieval timestamp—not only text and a single score.
5. **Safety and provenance:** retrieved content is untrusted reference material; it may inform a proposal or explanation but cannot authorize execution or mutate scope, findings, or workflow without human gates.
6. **Provider isolation:** local retrieval remains the default; remote embedding/LLM calls require explicit policy and egress controls. Never mix incompatible embedding dimensions/providers in one collection.
7. **Operational separation:** avoid v2's shared-port collision and direct mutable access patterns; expose the KB through bounded application services and read-only MCP tools first.
8. **Evaluation:** create a query/evidence benchmark to measure retrieval quality, citation correctness, stale-source behavior, and prompt-injection resistance before changing ranking or embeddings.

### Recommended KB layers

```text
Source registry + provenance
        ↓
Immutable document/version store + content hashes
        ↓
Normalized chunks + metadata + safety classification
        ↓
Embedding/index profiles (local or approved remote, isolated)
        ↓
Hybrid retrieval and citation assembler
        ↓
Bounded RedSage consumers: mentor, planner context, reporting reference
```

### Sequencing decision

The first v3 implementation should be a **KB contract and adapter layer** around the preserved data, followed by evaluation and versioned ingestion. Do not start by replacing ChromaDB, changing the deterministic embedder, importing all v2 backend code, or connecting the KB directly to autonomous agent actions.

**Mapping:** F-45 through F-49 are updated from “preserve only” to **“preserve foundation + redesign as a governed v3 KB subsystem.”** F-29, F-30, F-32, F-33, and F-50 depend on this boundary.

**Detailed proposal:** `docs/KB_V3_SUBSCRIPTION_PROPOSAL.md` defines the proposed domains, entities, storage, retrieval contract, ingestion pipeline, Hermes gateway, subscription implications, migration phases, and acceptance criteria.

**Implementation started:** `KB/` now owns provider-neutral v3 contracts. The first test-driven slice is verified by `KB/tests/test_contracts.py`; Cohere indexing and the v2 read-only adapter are next.

**Resource intake approved for review:** `RESOURCES/README.txt` records the operator-approved Wave One categories, deferred categories, source checklist, collection separation, and ingestion order.

## v2 issues to avoid carrying forward

These were verified in the v2 audit and are migration constraints, not ignored details:

1. No authentication/authorization; loopback-only is not sufficient for a subscription product.
2. Report matrix differs between live report endpoints and exported snapshot regarding archived tasks.
3. Finding confirmation can replace the stored evidence link instead of validating the existing link.
4. Frontend dependencies use `latest` with no lockfile.
5. Database initialization/migrations run on every request.
6. `cohere` is imported at module load despite offline operation.
7. Test runs pollute the development database and artifact directory.
8. The KB HTTP API and application both default to port 8000.

## Change-control rule

For every v3 change that touches a mapped capability:

1. Identify the applicable `F-*` IDs in the change description or plan.
2. Update this file's status/destination if the mapping changes.
3. Record the v2 source files and v3 source files changed.
4. Add or update tests proving the behavior and safety invariants.
5. Record unresolved v2 defects that were intentionally fixed, redesigned, or deferred.
6. Do not mark a feature **Present** until execution/test/readback evidence exists.

## Next absorption sequence

1. Preserve and verify the KB foundation (already present; no vector mutation).
2. Create v3 domain model and policy boundaries for projects, scope, work units, evidence, findings, and audit.
3. Port evidence custody and safety gates before AI convenience features.
4. Port workflow methodology, Steps, planner, and human approvals.
5. Port mentor/Boss Brain as bounded read-only assistance.
6. Port reporting/export/import with resolved consistency rules.
7. Build the v3 UI and API over the verified domain contracts.
8. Add authentication, tenancy, billing, operations, and subscription controls only after the local-first core is trustworthy.
