# RedSage v3 Knowledge Base Proposal

## Decision summary

Build a new, governed KB architecture for RedSage v3 while preserving the v2 KB as a read-only compatibility corpus during migration.

The KB must support both:

1. **Local-first deployments** for an individual operator or private installation.
2. **Hosted Hermes-server subscriptions** with multiple customers, organizations, projects, billing plans, auditability, and strict data isolation.

Do not make ChromaDB the long-term system of record. Keep it behind an index adapter for compatibility and local retrieval, while the v3 logical model is designed around durable metadata, provenance, tenancy, policy, and reproducible indexing.

## Product goals

- Give users trustworthy, cited security and audit guidance.
- Keep customer evidence separate from reference knowledge by default.
- Allow an organization to maintain private playbooks and procedures.
- Support offline/local operation without requiring an external AI provider.
- Make hosted deployment safe for multiple organizations.
- Let Hermes act as a bounded interface to RedSage capabilities, not as an unrestricted KB administrator.
- Make every recommendation reproducible: source, version, chunk, retrieval profile, and policy context should be inspectable.

## Knowledge domains

### 1. Reference Knowledge

RedSage-maintained or approved public security references, standards, defensive guidance, and methodology material.

- Shared according to license and product policy.
- Immutable versions.
- Trust and safety classification.
- May be included in hosted plans according to entitlements.

### 2. Organization Knowledge

Private customer playbooks, internal standards, architecture conventions, and approved procedures.

- Tenant-owned.
- Never visible to another tenant.
- Optional sharing across projects within the same organization.
- Must have an owner, retention rule, and access policy.

### 3. Project Context

Project Brief, scope rules, methodology selection, approved assumptions, and project decisions.

- Project-scoped.
- Used to tailor retrieval and mentor/planner context.
- Exportable with the project according to the organization's policy.

### 4. Evidence

Operator-submitted logs, screenshots/attachments, artifacts, findings, and derived assets.

- Separate custody from all KB domains.
- Never indexed into shared Reference Knowledge automatically.
- Optional project-local search index only after redaction/classification policy.
- Retention, deletion, and export are customer-controlled operations.

### 5. Agent and Audit Records

Prompts, tool calls, retrieval receipts, approvals, policy decisions, and audit events.

- Not normal KB content.
- Stored as audit/event data with access controls.
- Retrieval receipts should point to KB versions/chunks without copying sensitive text unnecessarily.

## Proposed logical architecture

```text
                    RedSage v3 KB API
                           │
             ┌─────────────┴─────────────┐
             │                           │
      Retrieval service             Ingestion service
             │                           │
   ┌─────────┼─────────┐         ┌───────┼────────┐
   │         │         │         │       │        │
Lexical   Vector    Policy   Parse   Normalize  Classify
search    search    filter   version  + chunk   + approve
   │         │         │         │       │        │
   └─────────┴─────────┴─────────┴───────┴────────┘
                           │
        PostgreSQL metadata/system of record
        + pgvector or replaceable vector adapter
                           │
             Object storage for source files
                           │
        Local adapter: SQLite + ChromaDB compatibility
```

## Storage recommendation

### Hosted system of record

Use PostgreSQL for v3 application and KB metadata, with a replaceable vector-index adapter. `pgvector` is the preferred first hosted vector backend because it keeps tenant-aware metadata and vector records close to the relational system of record and simplifies backup, transactions, and deployment. The abstraction must allow a later dedicated vector/search engine if scale or retrieval requirements justify it.

Use S3-compatible object storage for original source files and large immutable artifacts. For local installations, use a filesystem/object-store adapter with the same logical contract.

### Local deployment

Support a local profile using:

- SQLite for metadata where appropriate.
- The preserved v2 ChromaDB collection through a compatibility adapter.
- Local filesystem storage for source documents and project evidence.
- Deterministic embeddings as the zero-key default.

The hosted and local profiles must expose the same domain contracts even if their physical stores differ.

## Core entities

### `kb_tenants`

Organization/customer boundary. Every private KB record must carry a tenant ID.

### `kb_sources`

Logical source identity: name, owner, license, origin, trust level, domain, ingestion policy, and status.

### `kb_source_versions`

Immutable snapshot of a source: content hash, collected time, parser version, safety classification, approval state, and retention metadata.

### `kb_documents`

A document within a source version: title, canonical locator, document hash, language, document type, and classification.

### `kb_chunks`

Normalized retrieval units: chunk hash, document ID, ordinal, text location, content classification, and token/character counts.

### `kb_index_profiles`

Embedding/index identity: provider, model, dimensions, distance metric, chunking version, and creation timestamp. A chunk must never be queried through an incompatible profile.

### `kb_chunk_vectors`

Vector/index adapter record tied to a chunk and index profile. Never treat the vector store as the authority for ownership or permissions.

### `kb_access_policies`

Visibility and use rules for reference, organization, project, and evidence content. Retrieval must enforce these rules server-side.

### `kb_ingestion_jobs`

Auditable ingestion state machine: requested, scanning, parsed, classified, awaiting approval, indexed, failed, or retired.

### `kb_retrieval_receipts`

Immutable or append-only record of a retrieval operation: actor/agent, tenant/project, query fingerprint, policy version, index profile, selected chunk IDs, score components, and timestamp. Avoid storing raw query text unless policy permits it.

## Retrieval contract

A v3 retrieval response should contain:

```json
{
  "query_id": "...",
  "index_profile": "local-deterministic-v1",
  "policy_version": "...",
  "citations": [
    {
      "source_id": "...",
      "source_version_id": "...",
      "document_id": "...",
      "chunk_id": "...",
      "title": "...",
      "locator": "...",
      "excerpt": "...",
      "trust_level": 3,
      "score": 0.82,
      "score_components": {
        "lexical": 0.40,
        "vector": 0.27,
        "metadata": 0.15
      }
    }
  ],
  "warnings": [],
  "retrieval_timestamp": "..."
}
```

A consumer must be able to distinguish:

- No relevant result.
- Result blocked by policy.
- Result from stale/retired material.
- Result from an unapproved source.
- Result from a lower-trust fallback.

## Ingestion pipeline

1. Register source and ownership.
2. Acquire content through an approved connector or local upload.
3. Hash the raw input and create an immutable source version.
4. Scan for secrets, malicious content, unsafe instructions, and licensing metadata.
5. Parse and normalize using a pinned parser version.
6. Chunk deterministically and record chunking configuration.
7. Classify content and assign trust/use policy.
8. Require human approval for private, high-risk, or externally acquired content where policy requires it.
9. Generate embeddings using an isolated index profile.
10. Validate index counts, hashes, and sample citations.
11. Publish the version atomically.
12. Record an ingestion receipt and retain the previous active version until replacement is verified.

Failed ingestion must not partially publish a new version.

## Retrieval pipeline

1. Authenticate the actor and resolve tenant/project context.
2. Apply purpose and access policy before retrieval.
3. Query lexical and vector indexes separately.
4. Apply metadata, trust, freshness, and scope-aware boosts.
5. Rerank only within the permitted corpus.
6. Enforce result and excerpt limits.
7. Assemble citations from immutable IDs.
8. Mark untrusted content boundaries before any model call.
9. Write a retrieval receipt.
10. Return citations and safety warnings to the bounded consumer.

## Hermes server integration

Hermes should call RedSage through a narrow tool gateway such as:

- `redsage_kb.search` — retrieve permitted, cited context.
- `redsage_kb.get_source` — inspect approved source metadata, not arbitrary files.
- `redsage_kb.ingest_request` — create an ingestion request, never silently publish.
- `redsage_kb.review_ingestion` — human approval action where authorized.
- `redsage_kb.rebuild_index` — controlled operational action with approval and receipt.
- `redsage_kb.retrieval_receipt` — retrieve the explanation for a prior result.

The Hermes agent must not receive direct database credentials, raw object-store credentials, unrestricted SQL, or an unrestricted filesystem tool for customer data.

KB retrieval can inform a plan or answer. It cannot independently:

- Unlock or expand scope.
- Confirm a finding.
- Approve a proposal.
- Execute a security tool.
- Send customer communications.
- Delete customer data.

## Subscription model implications

### Free/local tier

- Local deterministic retrieval.
- Preserved/reference corpus.
- One operator or one local workspace.
- Limited indexed private documents.
- No hosted retention requirement.

### Professional tier

- Hosted organization workspace.
- Private organization KB.
- More indexed documents and retrieval volume.
- Persistent retrieval/audit history.
- Project exports and retention controls.

### Team/Enterprise tier

- Multiple users and roles.
- Separate organization collections and policy administration.
- SSO/SCIM later.
- Custom retention and residency.
- Private connectors and approval workflows.
- Dedicated index/profile or deployment option.

Enforce entitlements at the domain service, not only in the UI. Meter retrievals, ingestion volume, storage, and remote embedding usage using auditable usage events.

## Security requirements

- Tenant ID must be mandatory for all private records and checked server-side.
- Prefer database row-level security in hosted PostgreSQL, backed by application checks and tests.
- Never include `.env`, provider keys, or unrelated tenant data in exports.
- Encrypt hosted transport and storage; define key ownership before launch.
- Treat every source, chunk, query, and model response as potentially untrusted.
- Redact secrets before remote embedding or LLM calls.
- Support deletion and retention workflows with audit receipts.
- Prevent cross-tenant retrieval through negative tests, not assumptions.
- Keep reference licenses and attribution attached to citations and exports.

## Initial corpus and ongoing update policy

The first v3 KB corpus will be built from one user-provided book focused on structured problem-solving for bug hunters and penetration testers. The book will be ingested as an immutable, versioned source and converted into both cited searchable chunks and reviewed structured workflow knowledge.

The KB is a living product asset. Future updates will use the same controlled pipeline rather than editing indexed content in place:

```text
New or revised source
        ↓
Immutable version + hash
        ↓
Extract, normalize, classify, and review
        ↓
Cohere embedding in a new isolated index version
        ↓
Evaluation and citation verification
        ↓
Human approval
        ↓
Publish new active version; retain prior version for rollback
```

Every KB update must record the source/version, changed content, parser/chunker version, embedding profile, approval decision, verification results, and rollback target. Existing published versions remain available until the replacement is verified. Customer evidence is never silently merged into the shared book-derived corpus.

## Migration plan from v2

### Phase 1 — Compatibility

- Freeze the v2 KB data as read-only.
- Build a v3 `KnowledgeRepository` interface.
- Adapt the current `KBEngine` behind that interface.
- Preserve deterministic embedding compatibility.
- Add retrieval-contract tests and citation receipts.

### Phase 2 — Domain metadata

- Add source, version, document, chunk, index-profile, and ingestion-job models.
- Import v2 metadata without mutating the preserved ChromaDB vectors.
- Record hashes and mark imported records as legacy-compatible.

### Phase 3 — Hybrid v3 retrieval

- Add relational lexical search and a vector adapter.
- Return structured citations and score components.
- Add policy filtering and tenant/project context.
- Benchmark against v2 queries before changing ranking.

### Phase 4 — Versioned ingestion

- Implement local upload and controlled connectors.
- Add immutable versions, deterministic chunking, classification, approval, and atomic publish.
- Add re-index and rollback operations.

### Phase 5 — Hermes gateway

- Expose bounded read-only retrieval first.
- Add ingestion requests and human approval separately.
- Add retrieval receipts to agent conversations and audit records.

### Phase 6 — Hosted subscription hardening

- PostgreSQL deployment profile.
- Tenant isolation and negative tests.
- Authentication, roles, quotas, usage events, retention, billing hooks, and operational monitoring.

## Decisions intentionally deferred

- Whether to use a dedicated search engine alongside PostgreSQL.
- Which hosted embedding provider, if any, is permitted by plan and region.
- Encryption key management and customer-managed keys.
- Exact subscription quotas and pricing.
- Whether evidence may be opt-in indexed for project-local search.
- SSO/SCIM and enterprise deployment model.

## Acceptance criteria for calling the new KB ready

- Existing v2 queries remain available through the compatibility adapter.
- No preserved vector data is modified during migration.
- Every returned citation identifies source, version, document, and chunk.
- Tenant and project policy filtering is enforced server-side.
- Cross-tenant retrieval tests pass.
- Ingestion failures do not publish partial versions.
- Every index profile records provider, model, dimensions, and metric.
- Remote calls are explicit, redacted, and policy-controlled.
- Hermes tools cannot mutate scope, findings, workflow, or evidence without separate RedSage gates.
- Retrieval and ingestion operations produce auditable receipts.
- Local mode works without an API key.
