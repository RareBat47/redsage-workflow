---
name: project-context-mcp-rollout
description: Use when bootstrapping project context and MCP tools.
version: 0.1.0
author: RedSage operator, Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    editorial_name: Project Context and MCP Rollout
    editorial_description: Bootstrap project instructions, wire local MCP servers, and verify the live tool surface.
    tags: [project-context, mcp, onboarding, verification, rollout]
    related_skills: []
---

# Project Context and MCP Rollout Skill

Bootstrap an agent operating layer and connect local MCP servers without confusing written configuration with a working runtime. This workflow is for repository onboarding and tool-surface verification; it does not implement product features or silently broaden permissions.

## When to Use

- A repository needs `SOUL.md`, `AGENTS.md`, skills, internal context, or MCP wiring.
- A blueprint specifies a staged context/tool rollout.
- A local MCP server must be proven through discovery before the agent relies on it.

Do not use this skill for product-ticket implementation, provider troubleshooting, or a one-off MCP server whose configuration is already proven.

## Prerequisites

- Repository root and its source-of-truth documents.
- Explicit constraints for forbidden paths and allowed write zones.
- Project interpreter or runtime command for the local MCP server.
- Hermes CLI available for `mcp add`, `mcp list`, and `mcp test`.

## Procedure

1. **Recon before writing.** Read the supplied blueprint, existing `SOUL.md`, `AGENTS.md`, progress log, source-of-truth docs, and current skill files. Inspect the repository tree and git status.
   - Completion: list existing files, missing files, forbidden zones, current changes, and the intended rollout order.
2. **Separate policy from implementation.** Put identity and behavioral defaults in `SOUL.md`; put repository facts, safety constraints, gates, and guarded zones in `AGENTS.md`; put repeatable procedures in class-level skills; keep internal summaries concise.
   - Completion: no behavioral rule is duplicated across the two context files, and no unsupported feature is stated as fact.
3. **Create only gaps.** Create missing directories and files; preserve existing progress history and unrelated user changes. If a progress file must be updated, read or copy the complete existing content before appending.
   - Completion: every requested file is present, prior progress entries remain intact, and the diff contains no accidental truncation.
4. **Pin local MCP execution to the project runtime.** Register the server with Hermes using the project interpreter, module entry point, and repository working directory. Disable server-initiated sampling unless it is explicitly required and trusted.
   - Completion: the saved configuration contains the intended command, module, cwd, timeout, and tool policy without secrets in documentation.
5. **Verify in layers.** First import the MCP module and exercise its underlying capability directly. Then run Hermes discovery and confirm every expected tool name. Finally run `hermes mcp test <name>` and require a live connection plus discovered tools.
   - Completion: a written config is never treated as success; each layer has a real exit result.
6. **When the project is being productized, classify preserved subsystems before porting them.** Mark each capability as compatibility foundation, governed v3 domain, redesign, defer, or reject; record the source files, destination contract, safety implications, and acceptance evidence in a living migration register.
   - Completion: no v2 subsystem is copied wholesale, and every v3 feature change can be traced back to its mapped v2 behavior.
7. **For a KB intended for both local Hermes and hosted subscriptions, separate reference knowledge, organization knowledge, project context, evidence, and audit records before designing storage.** Keep customer evidence out of shared knowledge by default because tenancy, retention, deletion, and export rules differ.
   - Completion: each domain has explicit custody, visibility, retention, provenance, and allowed agent actions.
8. **Treat the vector store as an index, not the hosted system of record.** Keep durable source/version/document/chunk metadata, tenant policy, ingestion state, and retrieval receipts in the authoritative relational layer; use a replaceable vector adapter and preserve a local compatibility adapter for legacy ChromaDB data.
   - Completion: retrieval remains reproducible and tenant-filterable without depending on provider-specific vector metadata.
9. **Design KB retrieval and ingestion as bounded, auditable contracts before connecting Hermes.** Return source/version/document/chunk citations, score components, trust and freshness signals, and policy/index identities; make ingestion versioned, approval-aware, and atomic.
   - Completion: an agent can explain why context was returned, but cannot use KB content alone to expand scope, confirm findings, approve workflow, execute tools, or delete customer data.
10. **For a roadmap-generation KB, stage resources in a purpose-named folder and build a pre-embedding manifest before any provider spend.** Use approved categories first (methodology source, verified product docs, OWASP, CWE/CVSS, web platform docs, scope/stop policies), record licenses and hashes, select documentation-only files, chunk them, and report source/chunk counts with `embedding_status=not_embedded` before calling Cohere.
   - Completion: the user can review the exact candidate corpus and chunk count before credits are used or a vector collection is published.
11. **Do not download copyrighted books from public GitHub mirrors for subscription KBs.** Public availability is not usage permission; require a legally obtained upload or verified open-access source, and mark commercial redistribution/embedding rights separately from inspection access.
   - Completion: unofficial book mirrors are recorded as rejected sources, while approved free sources such as PTES/OWASP are downloaded with source manifests and rights caveats.
12. **Handle connection-close failures by checking launch context first.** Verify the server cwd and interpreter before changing code or blaming the MCP SDK. A module that imports from the repository root can close immediately when launched from another cwd.
   - Completion: the standalone test succeeds with the same command and cwd stored in Hermes configuration.
7. **Explain non-E2E test telemetry before reporting a green gate.** Run collection both with and without the marker filter, then run the filtered suite with `-rs` to capture every skip reason.
   - Completion: every deselected test is tied to the explicit marker expression, and every skip has its declared reason; do not treat unexplained exclusions as a pass.
8. **Keep active progress compact after rollout.** Archive completed receipts under `docs/internal/archive/` and leave the active progress file with current state, latest verification, operating decisions, and the next action.
   - Completion: historical detail remains retrievable while the working context stays short.
9. **Run project gates after executable changes.** Use the project interpreter for backend compile/tests and run the frontend build when applicable. Keep E2E opt-in unless the project explicitly says otherwise.
   - Completion: compile, tests, build, and any skipped E2E gate are reported with exact commands and real outcomes.
10. **Checkpoint and reload.** Append a concise receipt to the project progress log, including verified tools, failures that remain, and the next action. Restart Hermes when context or MCP discovery is startup-scoped; do not claim the current session has new tools until a fresh session proves it.
   - Completion: progress is auditable and the fresh runtime sees the intended context/tool surface.

## Pitfalls

- **Do not overwrite a progress log after reading only a paginated slice — the omitted history is still part of the artifact, so a rewrite can silently destroy it.** Preserve the complete file before appending.
- **Do not call native MCP registration complete because `mcp add` saved a config — discovery and a standalone `mcp test` are separate runtime checks.** Require both connection success and expected tool names.
- **Set the MCP server cwd explicitly — repository imports can fail or the stdio process can close when launched from Hermes’ install directory instead of the project root.**
- **Use the project interpreter in the MCP command — an ambient interpreter can pass a version check while lacking the repository dependencies.**
- **Record failed verification honestly and keep it in the checkpoint — a retry that later succeeds teaches the repair sequence, not that the first failure never happened.**
- **Keep KB-derived material inert and safe — a security KB can contain offensive text even when the MCP transport is functioning.**
- **Quote shell command paths and set a native `cwd` for Windows workspaces with spaces — process argument parsing and repository-relative imports otherwise diverge between an interactive shell and the MCP runner.**
- **Put mandatory proactive tool use in project rules when a domain requires it — an available MCP tool alone does not reliably prevent schema/API invention.**

## Verification

A successful rollout has all of these receipts:

- Context files and class-level skills exist and are readable.
- Forbidden repository zones have no changes.
- The MCP module imports with the project runtime.
- Hermes lists the server enabled.
- `hermes mcp test <name>` connects and discovers every expected tool.
- Applicable compile, test, and build gates pass.
- The progress log preserves prior history and records the current receipt.
