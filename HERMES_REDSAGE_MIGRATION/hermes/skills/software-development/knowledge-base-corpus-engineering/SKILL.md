---
name: knowledge-base-corpus-engineering
description: "Use when building or updating a governed KB corpus."
version: 1.0.0
author: RedSage operator, Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    editorial_name: Governed Knowledge-Base Corpus Engineering
    editorial_description: Build a licensed, provenance-preserving, evaluation-driven KB corpus for RedSage workflow generation.
    tags: [knowledge-base, corpus, ingestion, provenance, embeddings, cohere, github, licensing, workflow-generation]
    requires_tools: [terminal, file, web]
    requires_toolsets: [terminal, file]
    requires_plugins: []
---

# Governed Knowledge-Base Corpus Engineering

Build and maintain RedSage knowledge bases as controlled, reproducible corpora—not as indiscriminate downloads or unreviewed vector dumps. The target use case is workflow generation from a pasted, authorized pentesting problem statement: clarification, scope gates, ordered phases, hypotheses, tasks, evidence expectations, stop conditions, human approvals, and cited reasoning.

## Always-on rules

- **Get approval for specific sources before downloading or embedding them.** A category approval is not approval for every repository, book, write-up, or dataset inside that category.
- **Treat GitHub availability as discovery, not permission.** Record and verify the exact license, attribution, ShareAlike/copyleft obligations, commercial-use terms, owner, revision, and intended hosted-subscription use before ingestion.
- **Separate source preservation from derived workflow knowledge.** Keep the original source and immutable metadata intact; create separately reviewed chunks, workflow patterns, decision rules, and evidence guidance.
- **Use explicit namespaces by purpose.** Keep real-engagement methodology, RedSage product/domain rules, lab/CTF material, private organization knowledge, project context, and customer evidence separate; lab material is down-ranked or excluded for real-engagement queries.
- **Never ingest secrets or customer data into a shared corpus.** Exclude API keys, credentials, tokens, private keys, PII, `.env` files, raw customer evidence, and development clutter; do not print secrets while checking configuration.
- **Do not let retrieval authorize action.** KB content can inform a plan or explanation, but it cannot expand scope, confirm findings, approve workflow changes, execute tools, communicate with customers, or delete data.
- **Do not spend embedding credits before inspection.** First verify file structure, extraction quality, licensing, safety classification, expected chunk count, and operator approval; then estimate cost and process in resumable batches.
- **Do not call a download complete after a timeout or partial checkout.** Verify repository completeness, revision, license files, and selected content before adding it to the usable manifest.
- **Keep an auditable manifest.** Every source record includes URL/path, exact revision or edition, license evidence, content hash, source type, namespace, intended purpose, processing status, and verification result.
- **Prefer official and primary sources.** Use official standards, project repositories, vendor documentation, and clearly authorized write-ups; treat community repositories as supplementary and review their maintenance, ownership, duplication, and safety.
- **Use bounded workflow guidance.** Favor methodology, reasoning, authorization, validation, evidence, reporting, remediation, and stop/escalation logic; exclude executable code and operational material that would turn the KB into an autonomous offensive mechanism.
- **Present the exact candidate source list before downloading broad resource categories.** The operator wants to evaluate specific books, repositories, and documents; category approval alone is not sufficient for retrieval or ingestion.
- **Report partial downloads as partial and keep an explicit manifest.** If a large clone times out, retain it as incomplete/unusable until revision, completeness, license, and selected-file scope are verified; do not describe an attempt as a completed download.
- **Use a purpose-based resource tree.** Store workflow-generation inputs under `RESOURCES/WORKFLOW_GENERATION/<category>/`, keep raw sources separate from selected/normalized content, and maintain a download manifest with exact URLs, revisions, hashes, and statuses.
- **Start with a user-provided methodology book, then validate retrieval on a narrow web-application corpus.** The first-wave target is roadmap generation, so defer tools, broad platform coverage, private examples, and restricted standards until the core methodology retrieval is evaluated.
- **Treat the Cohere credential as local secret configuration only.** Never save, repeat, print, copy, or embed a key supplied in chat; use local secret configuration and report only presence/absence before provider operations.
- **Resolve project-local secrets by absolute project path in background jobs.** Load the project `.env` from the adapter/module location rather than relying on the child process working directory, because background shells may start elsewhere.
- **Serialize Chroma collection metadata to scalar values.** Store nested index profiles as deterministic JSON strings, because Chroma metadata accepts scalar metadata values rather than arbitrary nested dictionaries.
- **Make the build entry point importable and test it before running a live provider job.** A missing module or contract mismatch should fail in the local test cycle rather than after network calls and embedding spend.
- **Verify completion from independent artifacts, not process exit alone.** Match the receipt vector count to the manifest and live collection count, verify the recorded dimensions, run a real retrieval query, and inspect citation metadata before claiming the KB is built.
- **Do not call a core index complete when integration layers are absent.** Distinguish indexed-corpus completion from retrieval-service, evaluation, bounded-tool, and roadmap-consumer completion so status reports do not overclaim.
- **Execute the next non-blocked implementation step instead of only describing it.** After identifying an incomplete KB layer, write the smallest test first, implement it, run the test, and continue until a user decision or genuine external blocker remains.
- **When the user says “go on,” “do it,” or asks for next steps, perform the next non-blocked KB implementation slice immediately.** Do not repeat a plan as if it were progress; write the failing test, implement the slice, run the relevant tests, and continue until a real decision or external blocker remains.
- **Use the existing RedSage v2 planner UI as a presentation reference, not as a v3 implementation contract.** Preserve the useful clarification → expandable phase → task → Step → evidence → Apply/Discard flow, but add v3 safety state, query classification, citations, receipts, and explicit internal-only status.
- **Keep the current goal internal and operator-facing when the user has deferred customer-facing roadmap work.** Do not report missing customer UI, tenancy, billing, or subscription entitlements as blockers for internal KB retrieval and roadmap generation.
- **Diagnose provider failures at the network layer before changing corpus code.** Distinguish missing credentials, rejected requests, DNS resolution, TLS, timeout, and quota failures; a `getaddrinfo`/TLS failure means no embeddings were produced and the collection must not be reported as complete.
- **Do not expand scope from “internal KB” to “customer-facing roadmap” without an explicit user decision.** Internal retrieval quality, citations, receipts, and bounded Hermes access can be completed independently of hosted product, billing, or multi-tenant work.
- **Evaluate retrieval behavior, not just availability.** A query returning citations is insufficient; inspect whether scope/stop policy outranks technical guidance, whether lab content is separated, and whether the query is correctly classified before declaring quality improvements complete.
- **Harden shared retrieval before adding another corpus.** Consolidate normalization, policy filtering, ranking, citations, receipts, and index validation first, because duplicating those layers across domains multiplies drift and can require re-indexing.
- **Gate authorization before provider or vector work.** For an ambiguous problem statement, return clarification questions and skip Cohere/Chroma retrieval; this avoids unnecessary spend and prevents an unhealthy index from masking the safety decision.
- **Make metadata policy-authoritative at index time.** Persist approval, safety, scope, provenance, domain, and classification metadata in the index; path-based inference is only a compatibility fallback and must not silently promote unknown content.
- **Keep test-first implementation honest.** Write the failing test for each missing KB layer, run it to observe the expected failure, then implement the smallest passing behavior and rerun the full KB suite.
- **Run multi-collection Chroma evaluations in isolated subprocesses when the local backend shows segment-reader instability.** Fresh processes prevent Rust/HNSW state from leaking between collection queries and make failures reproducible.
- **Require a declared collection name in every real preview manifest.** Validate manifest identity against the requested collection before embedding so a receipt and vector store cannot silently refer to different artifacts; only minimal unit-test fixtures may omit it.
- **Reconcile manifest hashes separately from vector identity.** If a manifest is regenerated without changing chunk IDs, record the new hash and compare it to the historical build receipt rather than rewriting history or unnecessarily re-embedding.
- **Use one consolidated retrieval path for cross-KB workflows.** Domain facades may add query prefixes or domain labels, but normalization, filtering, ranking, citations, receipt fields, and index validation must remain shared to prevent behavioral drift.
- **Namespace cross-KB citation identities.** Keep the original chunk ID for source provenance, but key citations and receipt score maps by `<kb_domain>:<chunk_id>` so duplicate IDs from different collections cannot overwrite one another.
- **Treat a successful live query as an integration test, not a quality verdict.** Inspect the top paths, domain distribution, policy filtering, citation metadata, and receipt fields for representative queries before declaring the consolidated workflow improved.
- **When a hardening change breaks fixture assumptions, update the fixture contract rather than weakening production safety.** Test doubles must include the same safety metadata required by real indexed records; do not restore fail-open defaults just to keep old mocks green.

## Procedure

### 1. Define the retrieval job and corpus boundaries

Write down what a successful answer must produce and what it must never do. For RedSage Wave One, the output is a cited initial roadmap for an authorized web-application assessment. Define namespaces before downloading:

```text
reference_methodology
redsage_domain
web_app_standards
taxonomy_severity
scope_authorization
web_platform_docs
community_methodology
responsible_writeups
lab_ctf
```

Keep deferred categories out of the first corpus unless separately approved: tool documentation, broad cloud/mobile/network material, private examples, governance/legal content, unlicensed standards, and full vulnerability feeds.

### 2. Create a purpose-based resource tree

Use a stable structure that makes intended use visible in the path:

```text
RESOURCES/WORKFLOW_GENERATION/
├── 01_methodology_book/
├── 02_redsage_domain/
├── 03_owasp/
├── 04_cwe_cvss/
├── 05_web_platform_docs/
├── 06_github_methodology/
├── 07_writeups/
├── 08_lab_ctf/
├── 09_scope_authorization/
└── 10_stop_escalation/
```

Place manifests and approval records alongside the corpus, not in chat-only notes. Do not mix raw downloads with normalized or approved chunks.

### 3. Approve and review candidates

For each proposed source, record:

- Exact URL, repository, file, book title/edition, or document revision.
- Why it serves workflow generation.
- Source type and environment scope.
- License or written permission, including commercial redistribution implications.
- Attribution and ShareAlike obligations.
- Owner/contact for takedown or rights questions.
- Safety and privacy review result.
- Expected namespace and retrieval behavior.

For GitHub candidates, inspect the repository README, license, current commit, maintenance signal, file scope, and whether the content is documentation or executable code. Do not recursively ingest a repository merely because it is relevant.

### 4. Download reproducibly and defensively

Prefer shallow or sparse clones for large repositories, then verify the result:

```bash
git clone --depth 1 <url> <destination>
git -C <destination> rev-parse HEAD
git -C <destination> status --short --branch
find <destination> -maxdepth 1 -type f -iname 'LICENSE*' -o -iname 'README*'
```

For large repositories, use a filtered/sparse checkout only when the selected paths are known. If a clone times out, retain it as incomplete, mark it unusable, and retry with a smaller scope or direct raw/archive download. Never report a partial checkout as complete.

Copy internal RedSage documentation only from verified source files and exclude secrets, databases, artifacts, caches, and unrelated development data.

### 5. Inspect before embedding

For books and documents:

- Identify whether text extraction is reliable or OCR is needed.
- Preserve chapter, section, subsection, page, table, and heading locators.
- Detect duplicate, boilerplate, and navigation content.
- Scan for credentials, PII, unsafe operational content, and prompt-injection text.
- Produce an extraction report for human review.

For repositories:

- Select documentation, checklists, templates, and safe structured guidance.
- Exclude scripts, binaries, wordlists, secrets, generated output, and unrelated files unless explicitly approved.
- Preserve commit and path provenance for every selected file.

### 6. Derive workflow knowledge without losing the source

Convert approved material into two linked products:

1. **Cited source chunks:** text-preserving retrieval units with source/version/document/chunk IDs, heading path, page or path locator, content hash, trust, safety class, and license metadata.
2. **Structured workflow records:** problem classifications, clarification questions, prerequisites, hypotheses, ordered phases, tasks, Steps, expected evidence, stop conditions, escalation rules, and reporting fields.

Never replace a source passage with an uncited model summary. A structured record must link back to one or more exact source locators.

### 7. Embed with explicit provider profiles

When Cohere is approved and configured locally, record a separate index profile containing provider, model, document/query input types, dimensions, distance metric, chunker version, and timestamp. Use `search_document` for corpus chunks and `search_query` for user queries. Do not mix Cohere vectors with deterministic v2 vectors or different dimensions in one collection. Load the project-local secret by absolute path in the embedding module, and serialize nested profile metadata before passing it to Chroma.

Process in bounded, resumable batches:

```text
pending → embedding → indexed → verified
                    ↘ failed/retry
```

Persist batch receipts and skip already verified content hashes. Do not place the API key in source, manifests, tests, logs, archives, or KB text; load it through a local secret mechanism and report only presence/absence.

### 8. Evaluate retrieval before publication

Create representative queries covering:

- Verify the actual retrieval-to-assembly path for demos and evaluations; a hand-written roadmap example is presentation evidence only, not generator validation.
- Keep milestone status granular: source collection, preview manifest, vector index, retrieval service, evaluation, bounded Hermes integration, roadmap consumer, and internal KB completion are separate gates.

Create representative queries covering:

- Ambiguous or incomplete authorization.
- Initial web-application engagement planning.
- Authentication/session/access-control problem statements.
- Evidence and severity questions.
- Irrelevant or out-of-scope requests.
- Explicit lab/CTF wording.

Check relevance, citation locator accuracy, source/namespace separation, trust and freshness behavior, stop-condition retrieval, refusal behavior, and offline fallback. Publish only after human review of samples and the manifest is complete.

### 9. Version and update without in-place mutation

Treat every new or revised source as an immutable version. Re-extract, reclassify, re-embed in a new index version, evaluate, and human-approve before switching the active pointer. Retain the previous active version for rollback and record changed hashes, parser/chunker versions, embedding profile, evaluation results, and approval receipt.

### 10. Update the RedSage migration register

Whenever a source or KB behavior affects a mapped v2 capability, update `docs/V2_V3_FEATURE_MAP.md` with the relevant feature IDs, source files, v3 destination, tests, and any v2 defect intentionally avoided. Keep the resource manifest, KB roadmap, master build plan, and implementation status consistent.

### 11. Report milestone status precisely

Use separate statuses for source collection, preview manifest, vector index, retrieval service, evaluation, bounded Hermes integration, roadmap consumer, and internal KB completion. Do not call the entire KB complete merely because vectors exist, and do not call an internal milestone incomplete because customer-facing UI or subscription infrastructure is deferred.

## Topical references

- `references/source-approval.md` — rights, safety, provenance, and candidate approval checklist.
- `references/retrieval-evaluation.md` — query set, namespace separation, citation, and publication gates.
- `references/operational-verification.md` — independent index, retrieval, receipt, and Hermes/MCP verification gates.

## Pitfalls

- **Download “everything” without a specific source manifest — broad repositories contain incompatible licenses, executable code, duplicated advice, and material outside the roadmap objective.** Approve and select files deliberately.
- **Use a search snippet as evidence of source content — snippets omit context and cannot establish licensing, safety, or citation accuracy.** Open and inspect the actual source.
- **Blend lab/CTF and real-engagement material — lab permissions and assumptions can leak into production roadmaps.** Enforce separate namespaces and query-time filtering.
- **Copy a provider key from one project to another — credentials can leak through files, logs, archives, or future source ingestion.** Configure the replacement locally and check only its presence.
- **Embed before reviewing extracted text — a bad parser, OCR artifact, or unsafe passage becomes expensive and difficult to remove after indexing.** Inspect and approve the extraction first.
- **Treat a single vector score as truth — lexical matches, trust, freshness, policy, and citation quality affect usefulness.** Retain score components and evaluate the complete retrieval contract.
- **Overwrite the active index during updates — failed ingestion or bad ranking then destroys the known-good rollback point.** Publish a new version atomically and retain the prior one.
- **Copy entire internal repositories into shared knowledge — tests, caches, artifacts, and implementation-only details create noise or expose sensitive data.** Select verified domain documents and tests intentionally.

## Verification

A source is usable only when:

- Its exact identity, revision/edition, rights, purpose, namespace, and hash are recorded.
- The downloaded content is complete and the selected files have been inspected.
- Sensitive and unsafe content has been handled according to policy.
- Source locators survive extraction and chunking.
- No embedding credits were spent before approval.
- The embedding profile and batch receipts are recorded.
- Retrieval samples return correct citations and respect namespace/policy boundaries.
- Human approval is recorded before publication.
- The prior active index remains available for rollback.
