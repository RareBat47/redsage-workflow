# RedSage v3 Knowledge Base Build Master Plan

**Status:** Approved planning baseline for future KB work
**Scope:** Internal, operator-facing security workflow assistant
**Customer-facing roadmap UI:** Deferred
**Primary local workspace:** `D:\HIGH LEVELS OF WORKS\RedSage_v3`
**Primary interpreter:** `C:/Python314/python`

## 1. Mission and operating boundary

RedSage v3 will use multiple purpose-specific, governed knowledge bases to help an authorized operator analyze security problem statements, plan assessment work, interpret operator-collected evidence, and produce traceable internal findings material.

The KBs are decision-support infrastructure. They are not autonomous pentesters and must not:

- Execute security tools or arbitrary commands.
- Open sockets or scan targets.
- Expand or infer authorization.
- Confirm findings without evidence and human review.
- Approve workflow changes.
- Send customer communications.
- Delete customer data.

All retrieved material is untrusted reference context. Scope, authorization, policy, and human approval remain RedSage-owned controls outside the KB.

## 2. KB portfolio

Build and maintain these as separate logical domains and, where useful, separate vector collections:

1. **Workflow/Roadmap Ideation KB** — `redsage_v3_workflow_cohere_v1` — built baseline.
2. **Web Application Assessment KB** — `redsage_v3_assessment_web_cohere_v1` — next build.
3. **API Assessment KB** — `redsage_v3_assessment_api_cohere_v1` — after Web Application validation.
4. **Identity and Session KB** — `redsage_v3_assessment_identity_cohere_v1` — initially a filter/sub-index of web assessment content.
5. **Authorization and Business Logic KB** — `redsage_v3_assessment_authorization_cohere_v1` — initially a filter/sub-index of web assessment content.
6. **Evidence, Findings, and Reporting KB** — `redsage_v3_evidence_reporting_cohere_v1` — next major supporting domain.
7. **Scope, Authorization, and Stop-Condition Policy KB** — `redsage_v3_policy_cohere_v1` — highest-priority governed policy layer.
8. **Lab and CTF Reasoning KB** — `redsage_v3_lab_cohere_v1` — isolated, lab-only, excluded by default.
9. **Technology and Platform Context KB** — `redsage_v3_technology_web_cohere_v1` — selected official Web Application references.
10. **RedSage Product and Domain Compatibility KB** — `redsage_v3_product_domain_v1` — verified v2/v3 behavior and safety rules.
11. **Organization-Private KB** — per-organization identifier — deferred until tenancy exists.
12. **Project Evidence and Engagement Context Index** — per-project identifier — deferred until v3 evidence custody exists.
13. **Retrieval and Audit Receipt Store** — `redsage_v3_retrieval_receipts_v1` — file-based baseline exists; durable domain later.

## 3. Build lifecycle for every KB

Every KB follows this lifecycle; no source is silently added directly to an active index.

```text
Define contract
    ↓
Select sources
    ↓
Verify rights and safety
    ↓
Download/copy to purpose folder
    ↓
Record source manifest and hashes
    ↓
Extract and normalize
    ↓
Classify and enrich metadata
    ↓
Human review/approval where required
    ↓
Build preview manifest
    ↓
Run local tests and estimate Cohere usage
    ↓
Embed with Cohere in batches
    ↓
Create isolated versioned index
    ↓
Verify count, dimensions, metadata, and citations
    ↓
Run retrieval/evaluation suite
    ↓
Publish active version
    ↓
Register bounded Hermes/MCP tool
    ↓
Write completion receipt and update this plan
```

## 4. Step 1 — Define the KB contract

Before implementation, create a plan file for the domain containing:

- Name and identifier.
- Exact purpose.
- Accepted input types.
- Expected output shape.
- Source categories.
- Environment scope.
- Trust policy.
- Safety policy.
- Tenant/project visibility.
- Collection/index profile.
- Citation requirements.
- Receipt requirements.
- Evaluation cases.
- Explicit non-goals.

The contract must state whether the KB produces:

- Planning guidance.
- Assessment objectives.
- Evidence interpretation.
- Remediation context.
- Reporting structure.

## 5. Step 2 — Source selection and rights review

### Preferred source order

1. Official standards and guidance.
2. Official project/vendor documentation.
3. Clearly licensed repositories.
4. User-provided material with documented rights.
5. Public write-ups only with permission or compatible license.

### Per-source record

Record:

- Source ID.
- Title.
- Author/organization.
- Source URL or supplied filename.
- Exact revision, tag, commit, or edition.
- License and commercial-use status.
- Attribution requirements.
- ShareAlike/copyleft conditions.
- Owner/contact for takedown or rights questions.
- Download/upload timestamp.
- Raw content SHA-256.
- Intended KB/domain.
- Environment scope.
- Trust level.
- Safety classification.
- Approval status.

GitHub availability is never treated as proof of commercial reuse rights. Copyrighted books must be supplied lawfully or acquired through a licensed path; unofficial mirrors are rejected.

## 6. Step 3 — Purpose-specific resource layout

Use a dedicated resource root for every KB:

```text
RESOURCES/
└── <KB_PURPOSE>/
    ├── 00_MANIFESTS/
    ├── 01_primary_methodology/
    ├── 02_official_standards/
    ├── 03_taxonomy/
    ├── 04_technology_docs/
    ├── 05_writeups/
    ├── 06_policy/
    ├── 07_labs/              # only for lab KBs
    ├── 08_extracted/
    └── 09_review/
```

Keep raw downloads separate from extracted/index-ready content. Never index a whole repository by default.

## 7. Step 4 — Safe extraction and normalization

For each approved source:

1. Detect file type.
2. Extract text with page/section preservation when applicable.
3. Normalize line endings and encoding.
4. Preserve heading hierarchy.
5. Preserve tables and list context.
6. Preserve URLs and source locators.
7. Remove build artifacts, images, fonts, lockfiles, binaries, and generated files unless specifically required.
8. Scan for credentials, tokens, private keys, PII, and target-identifying data.
9. Flag unsafe or operationally excessive material.
10. Record extraction tool and version.

Do not execute downloaded repository code.

## 8. Step 5 — Content classification

Each document/chunk receives explicit classes such as:

- `methodology`.
- `assessment_objective`.
- `authorization_scope`.
- `stop_condition`.
- `evidence_guidance`.
- `remediation`.
- `taxonomy`.
- `technology_reference`.
- `case_study`.
- `lab_reasoning`.
- `redsage_domain`.
- `unsafe_or_restricted`.

For each chunk, also record:

- `source_type`.
- `environment_scope`.
- `is_approved`.
- `is_unsafe`.
- `trust_level`.
- `policy_tags`.
- `tenant_id` or project scope where applicable.
- `source_version_id`.
- `document_id`.
- `title`.
- `locator`.
- `content_hash`.
- `metadata_schema_version`.

Unknown or ambiguous material fails closed and is not returned for authorized-engagement retrieval.

## 9. Step 6 — Deterministic chunking

Chunk by semantic boundaries rather than arbitrary byte slices:

- Heading plus associated content.
- Complete procedure or checklist unit.
- Table with its heading/context.
- Related list items.
- Page range for PDFs.

Default starting parameters:

- Maximum chunk size: approximately 2,200 characters.
- Overlap: bounded and derived from the maximum size.
- Stable source/document/chunk IDs.
- SHA-256 hash of normalized chunk text.

Every chunk must remain traceable to its source and locator.

## 10. Step 7 — Preview manifest and approval gate

Before Cohere use, generate a JSON preview manifest containing:

- Manifest version.
- Creation time.
- KB identifier.
- Source count.
- Document count.
- Chunk count.
- Source hashes.
- Chunk hashes.
- Full metadata.
- Exclusion/review diagnostics.
- `embedding_status: not_embedded`.

The operator must be able to review the exact candidate corpus. No provider spend occurs before this checkpoint for new source batches.

## 11. Step 8 — Cohere embedding and index creation

Use the configured Cohere credential only through a secure local environment or vault; never place it in source, tests, logs, receipts, archives, or chat.

For approved content:

- Documents use `input_type=search_document`.
- Queries use `input_type=search_query`.
- Use controlled batches.
- Retry transient failures.
- Record progress.
- Do not duplicate completed vectors.
- Record actual model, dimensions, input types, metric, and profile ID.
- Keep each provider/model/dimension combination in an isolated collection.
- Never delete the previous verified collection during replacement.

Create a receipt containing:

- Manifest path and hash.
- Collection name.
- Vector count.
- Batch size.
- Model.
- Dimensions.
- Index profile.
- Metadata schema.
- Policy version.
- Build status.
- Timestamp.

## 12. Step 9 — Retrieval service

Every KB gets a bounded retrieval service with this flow:

```text
Validate input
    ↓
Classify query/problem
    ↓
Resolve environment and visibility
    ↓
Apply hard policy filter
    ↓
Generate Cohere query embedding
    ↓
Vector retrieval
    ↓
Lexical/metadata retrieval
    ↓
Bounded hybrid ranking
    ↓
Citation assembly
    ↓
Retrieval receipt
    ↓
Return structured context
```

Hard filtering occurs before ranking. Ranking must not bypass policy.

Recommended ranking inputs:

- Normalized vector similarity.
- Bounded lexical overlap.
- Heading/title relevance.
- Source trust.
- Freshness/version status.
- Query-class relevance.
- Explicit policy boosts.
- Lab penalty for real engagements.

Use deterministic tie-breaking.

## 13. Step 10 — Citation assembly

Every returned citation should include:

- Citation number.
- Source title.
- Author/organization.
- Source type.
- Source version/edition.
- Section/chapter/page or locator.
- URL/local source path.
- Source version ID.
- Document ID.
- Chunk ID.
- Excerpt.
- Content hash.
- Trust level.
- Approval/rights notice.
- Score and score components.

Unapproved or rights-review-required sources must be visibly labeled for internal review and must not be presented as approved shared content.

## 14. Step 11 — Retrieval receipts

Record a minimal, reproducible receipt for every retrieval:

```json
{
  "query_id": "qry_...",
  "actor_type": "operator|hermes|evaluation",
  "project_id": null,
  "query_hash": "...",
  "query_classification": "...",
  "environment_scope": "authorized_engagement|lab_only",
  "tenant_scope": null,
  "policy_version": "...",
  "ranking_profile": "...",
  "index_profile": "...",
  "candidate_count": 0,
  "filtered_count": 0,
  "filtered_reasons": [],
  "selected_chunk_ids": [],
  "score_components": {},
  "warnings": [],
  "created_at": "..."
}
```

Store query hashes by default, not raw problem statements. Retain raw text only under an explicit approved retention policy.

## 15. Step 12 — Domain-specific assessment outputs

For assessment KBs, each retrieved item should help answer:

- What is the assessment objective?
- What preconditions are required?
- What manual observation is relevant?
- What hypothesis is being evaluated?
- What evidence is minimally sufficient?
- What false positives should be checked?
- What would require stopping or escalation?
- What OWASP/CWE category may apply?
- What remediation context is relevant?
- What uncertainty remains?

The KB must separate:

```text
hypothesis ≠ observation ≠ verified finding
```

## 16. Step 13 — Evaluation suite

Each KB needs offline cases and live retrieval checks.

### Common cases

1. Authorized engagement with explicit scope.
2. Missing authorization.
3. Ambiguous scope.
4. Out-of-scope target.
5. Lab-only scenario.
6. Unsafe or destructive request.
7. Insufficient technology context.
8. Evidence too weak for a conclusion.

### Web assessment cases

- Authentication.
- Session management.
- Access control/IDOR.
- Input validation.
- Business logic.
- Browser/HTTP behavior.
- Evidence and remediation.

### API cases

- Object-level authorization.
- Function-level authorization.
- Schema/input validation.
- Rate limiting.
- Error behavior.
- Token/session handling.

Assertions must verify:

- Correct query classification.
- Correct policy behavior.
- Relevant citations.
- Source-type separation.
- Evidence and stop-condition presence.
- Absence of unsafe autonomous instructions.
- Deterministic receipt creation.

## 17. Step 14 — Hermes/MCP integration

Expose only narrow tools, for example:

- `search_workflow_kb`.
- `search_assessment_kb`.
- `get_kb_citation`.
- `get_retrieval_receipt`.

Do not expose:

- Raw database access.
- Unrestricted filesystem access.
- Customer object storage credentials.
- Direct index mutation.
- Workflow mutation.
- Scope or finding approval.

Verify in layers:

1. Python import.
2. Direct server startup.
3. MCP tool discovery.
4. Hermes registration.
5. Hermes MCP connection test.
6. New Hermes session.
7. Live bounded tool call.
8. Citation and receipt readback.

Disable server-initiated sampling unless explicitly required and trusted.

## 18. Step 15 — Versioning and update procedure

When adding or revising resources:

1. Register a new source/version.
2. Hash the raw content.
3. Extract and classify it.
4. Compare with the active version.
5. Review licensing and safety.
6. Generate a new preview manifest.
7. Run local tests and evaluation.
8. Create a new Cohere index version.
9. Verify counts, metadata, and retrieval.
10. Human-approve publication where required.
11. Switch the active profile.
12. Retain the previous profile for rollback.
13. Record the change receipt.
14. Update this master plan and the v2→v3 feature map.

Never edit published chunks in place as a substitute for versioning.

## 19. Build order

### Completed baseline

- KB-01 workflow/roadmap ideation collection.
- Cohere index with 3,219 vectors.
- Hybrid retrieval.
- Query classification.
- Policy filtering.
- Metadata refresh.
- Citation assembly.
- Retrieval receipts.
- Internal roadmap assembler and Markdown renderer.
- Bounded MCP server.
- Hermes MCP registration and connection test.

### Next

1. Persist richer source metadata in the active index and receipts.
2. Improve roadmap output evaluation beyond retrieval-only checks.
3. Build KB-02 Web Application Assessment Guidance.
4. Build KB-06 Evidence/Findings/Reporting support.
5. Deepen KB-04 Identity/Session and KB-05 Authorization/Business Logic.
6. Add only required Web Application technology references.
7. Build separate KB-08 Lab/CTF corpus.
8. Build KB-03 API Assessment Guidance.
9. Move receipts into durable v3 audit storage.
10. Add private/org/project indexes only after custody and tenancy boundaries exist.

## 20. Completion definition

A KB is complete for its stated milestone only when:

- Its contract is documented.
- Its sources and rights status are recorded.
- Its content is extracted and classified.
- Its preview manifest is reproducible.
- Its Cohere index is isolated and verified.
- Vector count matches the approved manifest.
- Metadata is explicit and policy-usable.
- Retrieval applies hard filters before ranking.
- Citations are human-readable and traceable.
- Receipts explain retrieval decisions.
- Evaluation cases pass.
- MCP integration is verified if required.
- No autonomous security action was introduced.
- The source/version/index receipt is recorded.
- The feature map and status documentation are updated.

## 21. User intervention points

Proceed automatically for:

- Local inspection.
- Source classification.
- Safe file selection.
- Hashing.
- Chunking.
- Tests.
- Manifest generation.
- Metadata-only refresh.
- Retrieval evaluation.
- Documentation.
- Bounded local code implementation.

Stop and request the user when required for:

- Specific copyrighted/private source approval.
- Commercial rights or licensing decisions.
- Secure credential entry or replacement.
- Cohere spend approval for a new corpus when the preview has not been reviewed.
- Scope or authorization decisions.
- Customer-data retention/deletion decisions.
- Irreversible reset/deletion.
- Product behavior decisions that materially change the domain contract.
