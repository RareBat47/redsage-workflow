# RedSage v2: Cohere-Powered Pentesting Companion

## 1. Executive Summary

RedSage v2 will preserve the existing ChromaDB knowledge base and SQLite data while replacing the placeholder answer generator with a grounded retrieval-augmented generation (RAG) workflow. The initial release will use the existing local embedder for ChromaDB retrieval, Cohere Rerank to select the strongest sources, and a configurable Cohere Command model to produce an answer linked to those sources.

The RAG workflow will be exposed through a Streamlit interface designed for authorized penetration-testing engagements. The interface will provide a visible scope lock, conversational guidance, inspectable citations, and a structured way to save findings and supporting evidence.

Target workflow:

```text
User query
  -> ChromaDB candidate retrieval
  -> Cohere Rerank
  -> Cohere grounded generation
  -> Answer with mapped source citations
  -> Optional finding or evidence save to SQLite
```

The first implementation will favor compatibility and low migration risk. Semantic re-embedding remains a separate, explicitly approved migration because the current and Cohere embedding dimensions are incompatible.

---

## 2. Verified Baseline

The existing stores are available and were successfully inspected before preparing this plan.

| Store | Current State | Relevant Contents |
|---|---:|---|
| ChromaDB (`data/chroma`) | Approximately 447 MB | `redsage_kb_local_v4`: 13,385 chunks; `redsage_kb_local_v3`: 17,600; `redsage_kb_local`: 12,751 |
| SQLite (`data/redsage.db`) | Approximately 18 MB | 11 tables, including `engagement`, `finding`, `artifact`, `kbsource` (17 rows), `kbdocument` (3,740 rows), and `usagelog` (6,030 rows) |

Current application behavior:

- [`core/kb_engine.py`](core/kb_engine.py) retrieves and ranks `Citation` objects but `grounded_answer()` only formats content from the first result.
- [`core/embeddings.py`](core/embeddings.py) reproduces the 8-dimensional deterministic embedding algorithm used by `redsage_kb_local_v4`.
- [`interfaces/api.py`](interfaces/api.py) calls `search()` and `grounded_answer()` independently.
- [`interfaces/mcp_server.py`](interfaces/mcp_server.py) exposes retrieval but does not generate an answer.
- The SQLite engagement and finding tables already contain the fields needed for scope and finding persistence. The `artifact` table stores file metadata and paths, not artifact content.

> [!NOTE]
> ChromaDB may update internal bookkeeping in `data/chroma/chroma.sqlite3` when a persistent client opens the store. The implementation must not re-ingest, delete, reset, or modify collection content as part of the default path.

---

## 3. Goals and Non-Goals

### Goals

1. Replace the placeholder answer formatter with a Cohere-backed RAG pipeline.
2. Preserve compatibility with the active `redsage_kb_local_v4` collection.
3. Return citations that can be traced to the exact retrieved ChromaDB chunks.
4. Provide a responsive Streamlit UI with session chat history and source inspection.
5. Require an active engagement scope before saving engagement evidence.
6. Persist structured findings safely in the existing SQLite schema.
7. Fail clearly and safely when configuration, retrieval, reranking, generation, or persistence fails.
8. Add deterministic tests for the core behavior without requiring live Cohere calls.

### Non-Goals for the Initial Release

- Re-embedding or deleting existing ChromaDB collections.
- Automatically executing payloads, shell commands, scans, or network requests.
- Treating the scope banner as a substitute for legal authorization or technical network controls.
- Building multi-user authentication, remote hosting, or collaborative engagement management.
- Changing the existing SQLite schema unless implementation proves that a schema change is necessary.
- Guaranteeing page-level citations when source chunks do not contain page metadata.

---

## 4. Required Decisions and Defaults

### 4.1 Embedding Strategy

The active collection, `redsage_kb_local_v4`, was built with the 8-dimensional `DeterministicEmbedder`. Cohere `embed-english-v3.0` produces 1,024-dimensional vectors. A query vector from one provider cannot be used against a collection built by the other.

#### Option A: Preserve the Active Collection (Initial Default)

- Continue using `DeterministicEmbedder` for ChromaDB candidate retrieval.
- Use Cohere only for reranking and answer generation.
- Leave all existing collections intact.
- Validate retrieval quality with a representative query set before release.

This option has the lowest migration risk, but the hash-based embedding is not semantic. Cohere can improve ordering only when a relevant chunk is present in the retrieved candidate set. If evaluation shows poor recall, increase the candidate pool within an acceptable latency limit or proceed to Option B.

#### Option B: Build a New Semantic Collection (Separate Migration)

- Re-embed the source corpus with a supported Cohere embedding model.
- Write to a new collection, such as `redsage_kb_cohere_v4`; never overwrite an existing collection.
- Add checkpointing, batching, retry handling, cost estimation, and document-count validation.
- Switch `REDSAGE_COLLECTION` and `REDSAGE_EMBEDDING_PROVIDER` only after quality and integrity checks pass.

The duration and API cost must be measured from the final corpus size, selected model, Cohere rate limits, and account pricing rather than assumed in advance.

### 4.2 Interface

The initial UI will use Streamlit. The existing FastAPI and MCP interfaces will remain available and must continue to import and run.

### 4.3 Scope Persistence

Scope will persist in the existing `engagement` table. A scope lock creates or activates one engagement; the active engagement is the most recently updated row whose status is `active`. Activating a new engagement will mark any previously active engagement as inactive in the same transaction.

### 4.4 Models

Rerank and generation model IDs will be configuration values rather than hard-coded constants. Initial defaults may use `rerank-v3.5` and an account-supported Command R model. Exact generation model availability must be verified against the installed Cohere SDK and target Cohere account during implementation.

---

## 5. Functional Design

### 5.1 RAG Contract

Add explicit result types so callers receive one coherent result instead of coordinating retrieval and generation themselves.

```python
@dataclass(frozen=True)
class GroundedCitation:
    chunk_id: str
    title: str
    source: str
    url: str
    text: str
    retrieval_score: float
    rerank_score: float
    spans: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class RagResult:
    answer: str
    citations: list[GroundedCitation]
    candidate_count: int
    model: str
```

The public method should validate input and own the complete workflow:

```python
def grounded_answer(
    self,
    query: str,
    *,
    top_k: int | None = None,
    rerank_top_n: int | None = None,
) -> RagResult:
    """Retrieve, rerank, and generate a source-grounded answer."""
```

Processing requirements:

1. Trim and validate the query; reject empty input and enforce a reasonable maximum length.
2. Retrieve up to `top_k` candidates from ChromaDB using the embedder associated with the active collection.
3. Return an explicit insufficient-context result when no candidates pass retrieval filtering.
4. Submit stable document IDs and chunk text to Cohere Rerank.
5. Keep at most `rerank_top_n` results and preserve both local and Cohere scores.
6. Submit only the selected documents to the generation model.
7. Instruct the model to answer from supplied context, identify uncertainty, and avoid inventing tools, commands, sources, or results.
8. Map Cohere citation document IDs and spans back to the original chunks; do not infer a citation that the response did not provide.
9. Return only cited source chunks in the final result, in first-reference order.
10. Avoid logging API keys, full prompts, sensitive targets, or complete generated answers by default.

Citation accuracy means source and chunk traceability. Page numbers should be displayed only when the corresponding metadata field is present.

### 5.2 Error Behavior

Use typed application exceptions or an equivalent stable error contract:

| Failure | Required Behavior |
|---|---|
| Missing API key | Stop before the API call and show a configuration-specific message |
| Missing or empty collection | Report the configured collection name and do not call Cohere |
| Cohere authentication error | Show an actionable credential error without exposing the key |
| Rate limit or temporary service error | Apply bounded retries with backoff, then report a retryable failure |
| Timeout | Use explicit client timeouts and preserve the user's query for retry |
| No relevant context | Return an insufficient-context answer with no fabricated citations |
| Citation mapping mismatch | Omit unmatched citations and record a sanitized diagnostic warning |
| SQLite write failure | Roll back the transaction and retain unsaved form content in session state |

The first release does not need an automatic non-Cohere answer fallback. Silent fallback would make answer quality and provenance unclear. Retrieval-only results may still be shown when generation fails.

### 5.3 Scope Model

Add [`core/scope.py`](core/scope.py) with a small persistence and matching API:

```python
class ScopeManager:
    def lock_target(
        self,
        title: str,
        targets: list[str],
        scope_notes: str = "",
    ) -> Engagement: ...

    def active_scope(self) -> Engagement | None: ...
    def in_scope(self, host: str) -> bool: ...
```

Implementation requirements:

- Support exact hostnames, wildcard subdomains such as `*.example.com`, individual IPv4/IPv6 addresses, and CIDR ranges.
- Normalize casing, whitespace, trailing dots, and IP representations before storage and comparison.
- Reject malformed or empty scope entries instead of accepting ambiguous text.
- Store a canonical, documented representation in the existing `target` field and human notes in `scope_notes`.
- Update engagement statuses atomically so only one engagement is active.
- Use parameterized SQL, enable SQLite foreign-key enforcement for each connection, and close connections deterministically.
- Treat `in_scope()` as a UI and persistence safeguard. It does not authorize or execute network activity.

### 5.4 Evidence and Finding Persistence

Add [`core/evidence.py`](core/evidence.py) to encapsulate writes to the existing schema.

The initial UI should save a `finding` row with all required fields:

- `engagement_id`: active engagement ID.
- `title`: concise user-provided title.
- `severity`: validated value from a fixed set such as informational, low, medium, high, or critical.
- `description`: analyst summary.
- `evidence`: selected answer, command, payload, response excerpt, or analyst-entered evidence.
- `affected_target`: normalized target that must pass `in_scope()`.
- `source_reference`: serialized IDs or URLs for cited KB chunks.
- `status`: initial value such as `draft`.
- `notes`: optional analyst notes.
- `created_at` and `updated_at`: UTC timestamps.

The `artifact` table should be used only when a real file is persisted because it stores a filename and path rather than inline content. Text-only scratchpad content belongs in `finding.evidence`. File artifacts, if included in the initial release, must use generated safe filenames, a dedicated application-managed directory, size limits, and path traversal protection.

All writes must be transactional. A failed save must not leave a partial finding or orphaned artifact row.

---

## 6. Implementation Phases

### Phase 1: Configuration and Dependencies

#### Modify [`core/config.py`](core/config.py)

Add and validate the following settings:

| Setting | Environment Variable | Default | Validation |
|---|---|---:|---|
| Cohere API key | `COHERE_API_KEY` or `CO_API_KEY` | unset | Required only for rerank/generation |
| Rerank model | `COHERE_RERANK_MODEL` | `rerank-v3.5` | Non-empty string |
| Generation model | `COHERE_GENERATE_MODEL` | supported Command R model | Non-empty string |
| Retrieval candidate count | `REDSAGE_TOP_K` | `15` | Integer from 1 to 100 |
| Rerank result count | `REDSAGE_RERANK_TOP_N` | `4` | Integer from 1 to `REDSAGE_TOP_K` |
| Request timeout | `COHERE_TIMEOUT_SECONDS` | `30` | Positive numeric value |

Configuration should fail early for invalid numeric ranges. It should not require a Cohere key for retrieval-only operations such as KB statistics and source listing.

#### Modify [`requirements.txt`](requirements.txt)

- Add a Cohere SDK version compatible with the selected chat and rerank APIs.
- Add `streamlit>=1.35`.
- Preserve the existing dependencies.
- Prefer a tested upper bound or lock file once the implementation is verified to reduce SDK breakage.

#### Add [`.env.example`](.env.example)

```ini
# Never commit a real API key.
COHERE_API_KEY=replace-with-your-key
COHERE_RERANK_MODEL=rerank-v3.5
COHERE_GENERATE_MODEL=replace-with-supported-command-model
COHERE_TIMEOUT_SECONDS=30

REDSAGE_COLLECTION=redsage_kb_local_v4
REDSAGE_EMBEDDING_PROVIDER=local
REDSAGE_TOP_K=15
REDSAGE_RERANK_TOP_N=4
```

Acceptance criteria:

- Existing local retrieval works without a Cohere key.
- RAG requests fail with a clear message when the key is absent.
- Invalid `top_k`, `rerank_top_n`, and timeout values are rejected at startup.
- `.env` remains excluded from source control if version control is initialized later.

### Phase 2: Core RAG Engine

#### Modify [`core/kb_engine.py`](core/kb_engine.py)

- Add `RagResult` and grounded citation result types.
- Initialize the Cohere client lazily so offline retrieval remains available.
- Implement private rerank and generation methods with explicit request timeouts.
- Replace the placeholder `grounded_answer()` behavior with the complete pipeline.
- Keep `search()`, `collection_stats()`, and `list_sources()` backward-compatible.
- Convert selected chunks to stable Cohere document IDs based on `chunk_id`.
- Preserve source metadata required by the UI and API.
- Limit document and prompt sizes to control latency and API usage.

#### Modify [`interfaces/api.py`](interfaces/api.py)

- Update `/api/ask` to call the new `grounded_answer(query, ...)` contract once.
- Return generation metadata and grounded citations without duplicating retrieval.
- Map known application errors to appropriate 4xx, 429, or 503 responses instead of returning every failure as HTTP 500.
- Keep `/api/health`, `/api/kb/sources`, and `/api/kb/stats` operational without a Cohere key.

#### Review [`interfaces/mcp_server.py`](interfaces/mcp_server.py)

- Preserve the existing `kb_search` retrieval tool.
- Optionally add a separate `kb_ask` tool using the RAG result contract; do not change `kb_search` semantics.
- Update the default `top_k` to read from configuration if that is consistent with existing clients.

Acceptance criteria:

- A successful answer includes at least one mapped citation when the model cites context.
- Every returned citation maps to a retrieved `chunk_id`.
- No-context behavior produces no invented source references.
- Existing retrieval, source-listing, and collection-statistics calls continue to work.
- Cohere failures do not corrupt or modify the knowledge base.

### Phase 3: Scope and Evidence Services

#### Add [`core/scope.py`](core/scope.py)

- Implement engagement creation, activation, lookup, and target matching.
- Reuse the existing schema and avoid migrations unless a concrete limitation is found.
- Document the canonical target serialization format.

#### Add [`core/evidence.py`](core/evidence.py)

- Implement validated, transactional finding creation.
- Add artifact persistence only if the UI supports actual file uploads.
- Return stable IDs to the caller after a successful commit.

Acceptance criteria:

- Activating a new engagement leaves exactly one active engagement.
- Exact hosts, wildcard hosts, IP addresses, and CIDRs match as documented.
- An out-of-scope affected target cannot be saved.
- A failed write rolls back completely.
- Existing engagement, finding, and artifact rows remain unchanged by tests through use of a temporary database copy.

### Phase 4: Streamlit Interface

#### Add [`app.py`](app.py)

Use a single Streamlit entry point for the initial release, while keeping business logic in `core/`.

```text
+---------------------------------------------------------------+
| RedSage | Active scope: *.example.com | Manage scope          |
+---------------------------------------------------------------+
| Conversation                                                  |
|                                                               |
| User question                                                 |
| Grounded answer with citation markers                         |
|                                                               |
| [Question input.....................................] [Ask]   |
+-------------------------------+-------------------------------+
| Sources                       | Finding draft                 |
| Expandable cited chunks       | Title, severity, target      |
| Source, URL, scores, metadata | Description and evidence     |
|                               | [Save draft]                  |
+-------------------------------+-------------------------------+
```

Required behavior:

- Display the active scope persistently and clearly distinguish a locked scope from an unset scope.
- Keep conversation and unsaved form state in `st.session_state`.
- Disable duplicate submissions while a request is running.
- Render model output as text or sanitized Markdown; never render arbitrary HTML from model or source content.
- Show citation markers linked to expandable source cards.
- Display source title, source name, URL when valid, chunk ID, and retrieval/rerank scores.
- Clearly label generated commands and payloads as suggestions that require analyst review.
- Require an active scope and an in-scope affected target before enabling the save action.
- Preserve the draft and display an actionable error if persistence fails.
- Do not execute generated commands or make requests to target systems.

Acceptance criteria:

- The app loads on desktop and remains usable at narrow browser widths.
- Chat history survives Streamlit reruns within the same session.
- Citation cards correspond exactly to citation markers returned by the engine.
- Scope changes are reflected immediately without losing the current finding draft.
- Saving a valid draft creates one finding row and reports its ID.

### Phase 5: Verification and Documentation

#### Add [`verify_rag.py`](verify_rag.py)

Provide an explicit live-service smoke test:

```powershell
python verify_rag.py
```

Default test query:

> What are the standard checks for IDOR under OWASP WSTG, and how should an authorized tester validate them?

The script should:

1. Print the active collection, embedding provider, candidate count, rerank model, and generation model.
2. Run one RAG request.
3. Print the answer followed by each mapped citation and score.
4. Exit nonzero when configuration, retrieval, citation mapping, or generation fails.
5. Avoid writing to ChromaDB collections or engagement tables.

#### Add automated tests

Use temporary databases and mocked Cohere responses so tests are repeatable and do not consume API credits. Cover:

- Configuration validation.
- Empty queries and no-result retrieval.
- Rerank ordering and `top_n` enforcement.
- Citation mapping, including unknown document IDs.
- Cohere authentication, timeout, and rate-limit handling.
- Scope normalization and matching.
- Transactional finding creation and rollback.
- FastAPI response contracts.
- Streamlit startup or a focused UI smoke test where practical.

#### Modify [`README.md`](README.md)

- Document environment configuration and the distinction between local retrieval and Cohere RAG.
- Add Streamlit startup instructions.
- Document data sent to Cohere and advise users not to submit secrets or unnecessary client-sensitive content.
- Explain the scope safeguard and its limitations.
- Document backup and recovery steps for `data/redsage.db`.

---

## 7. Verification Plan

### Pre-Implementation Safety Checks

```powershell
python inspect_db.py
```

- Record current collection and table counts.
- Back up `data/redsage.db` before testing persistence against the working database.
- Use a temporary ChromaDB fixture or retrieval mocks for destructive and failure-path tests.

### Automated Verification

```powershell
python -m pip install -r requirements.txt
python -m pytest
```

If the project does not add pytest, use the selected standard-library test runner consistently and update this command.

### Live Cohere Smoke Test

```powershell
python verify_rag.py
```

Expected result:

- The script retrieves candidates from `redsage_kb_local_v4`.
- Reranking returns no more than the configured top four chunks.
- The generated answer contains only mapped citations.
- The process exits successfully and reports model/configuration details without exposing credentials.

### Manual UI Verification

```powershell
streamlit run app.py
```

1. Confirm the app loads without an active scope and prevents evidence saving.
2. Lock a test scope containing an exact host, wildcard domain, and CIDR.
3. Submit the IDOR test query and confirm the answer and source cards render.
4. Confirm an out-of-scope target is rejected.
5. Save an in-scope finding draft and verify one correctly populated `finding` row exists.
6. Simulate a persistence error and confirm the draft remains visible.
7. Remove or invalidate the Cohere key and confirm retrieval-only views remain available while RAG shows a configuration error.

### Regression Verification

```powershell
python -m uvicorn interfaces.api:app --host 127.0.0.1 --port 8000
python -m interfaces.mcp_server
```

- Confirm FastAPI health, source, statistics, and ask endpoints behave as documented.
- Confirm existing MCP retrieval tools still start and return JSON.
- Compare post-test collection and source counts with the recorded baseline.

---

## 8. Security, Privacy, and Operational Controls

- Use RedSage only for systems covered by explicit authorization and the active engagement scope.
- Never store a real Cohere key in source files, logs, screenshots, or `.env.example`.
- Treat user queries and retrieved chunks as data sent to Cohere for reranking and generation; review organizational data-handling requirements before use.
- Do not send unrelated client secrets, credentials, tokens, or raw sensitive datasets to the model.
- Bind local development servers to `127.0.0.1` by default.
- Do not add command execution, automated scanning, or outbound target requests to this release.
- Use parameterized SQL and transactions for every write path.
- Sanitize filenames and validate paths if file artifact support is enabled.
- Apply bounded input sizes for questions, source documents, findings, notes, and uploads.
- Keep sanitized operational logs for errors and timing; do not log secrets or sensitive full-text content by default.

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hash-based retrieval misses relevant chunks | Reranker cannot recover documents absent from the candidate set | Benchmark representative questions; tune the candidate pool; use Option B if recall remains inadequate |
| Cohere model or SDK changes | Runtime failures or response-shape changes | Keep model IDs configurable, pin a tested SDK range, and test response adapters |
| Unsupported citation metadata | Misleading page-level attribution | Show page numbers only when metadata supplies them; always retain chunk IDs |
| API latency or rate limits | Slow or failed chat requests | Use timeouts, bounded retries, UI progress states, and clear retryable errors |
| Sensitive data sent to a third party | Privacy or contractual exposure | Display a data-handling notice and minimize submitted content |
| Concurrent SQLite writes | Lock errors or partial persistence | Keep transactions short, configure a busy timeout, and roll back on failure |
| Scope parsing ambiguity | Findings associated with unintended targets | Normalize supported formats and reject ambiguous entries |
| Accidental knowledge-base mutation | Loss or corruption of preserved data | Never overwrite collections; record baseline counts; retain backups; test writes on copies |
| Generated security guidance is unsafe or incorrect | Analyst error or unintended impact | Require human review, preserve citations, show uncertainty, and prohibit automatic execution |

---

## 10. Definition of Done

The initial release is complete when all of the following are true:

- The default collection remains `redsage_kb_local_v4` and its chunk count remains unchanged.
- `grounded_answer()` performs retrieval, reranking, generation, and citation mapping through one stable contract.
- Every displayed citation maps to a real retrieved chunk.
- Missing context and Cohere failures produce explicit, non-fabricated responses.
- FastAPI retrieval and health functionality remains operational.
- Streamlit supports scope management, chat history, source inspection, and structured finding saves.
- Finding writes require an active engagement and an in-scope affected target.
- Unit and integration tests pass without live API access.
- The live Cohere smoke test passes with a valid key.
- Database baseline checks show no unintended collection or table changes.
- Setup, configuration, privacy behavior, run commands, and recovery steps are documented.

---

## 11. Planned File Map

```text
RedSage_v2/
|-- .env.example              [NEW] Safe configuration template
|-- app.py                    [NEW] Streamlit interface
|-- verify_rag.py             [NEW] Live Cohere smoke test
|-- requirements.txt          [MODIFY] Cohere and Streamlit dependencies
|-- README.md                 [MODIFY] Setup, usage, privacy, and recovery
|-- core/
|   |-- config.py             [MODIFY] RAG configuration and validation
|   |-- embeddings.py         [REVIEW] Preserve provider/collection compatibility
|   |-- kb_engine.py          [MODIFY] Retrieval, rerank, generation, citations
|   |-- scope.py              [NEW] Engagement scope persistence and matching
|   `-- evidence.py           [NEW] Transactional finding/artifact persistence
|-- interfaces/
|   |-- api.py                [MODIFY] New RAG result and error contracts
|   `-- mcp_server.py         [REVIEW] Preserve search; optionally add RAG tool
|-- tests/                    [NEW] Deterministic unit and integration tests
`-- data/
    |-- chroma/               [PRESERVE] Existing collections; no re-ingestion
    `-- redsage.db            [PRESERVE + WRITE] Existing KB tables preserved;
                               engagement/finding/artifact rows written intentionally
```

## 12. Recommended Delivery Order

1. Confirm the Option A default and the supported Cohere generation model.
2. Add configuration validation and dependencies.
3. Implement and unit-test the RAG result contract.
4. Update FastAPI and verify regression behavior.
5. Implement and test scope persistence and target matching.
6. Implement and test transactional finding persistence.
7. Build the Streamlit interface on the tested core services.
8. Run automated tests and the live Cohere smoke test.
9. Complete manual UI and database-integrity verification.
10. Update user-facing documentation and record the final baseline counts.
