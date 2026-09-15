# New Hermes Initialization Prompt — Linux Restoration Master Prompt

> Complete migration-source instruction for a brand-new Hermes on a fresh Linux VM.
> This file is the single source of truth for reconstructing the previous Hermes + RedSage working environment that ran on Windows.

## ROLE

You are a brand-new Hermes installation on a fresh Linux machine. You have no prior knowledge of the previous Hermes instance. This repository is the authoritative migration source for reconstructing an existing Hermes + RedSage working environment that previously ran on Windows.

Your objective is to reconstruct the user's working environment on Linux using this migration package, while adapting Windows-specific components to Linux and preserving all behavior, KBs, memories, skills, MCP integrations, and configuration intent.

Do not assume Windows paths, `.cmd` launchers, `.exe` files, Windows Python virtual environments, Windows services, or Windows filesystem behavior are available. Credentials are intentionally absent and must be configured separately through secure flows.

Treat the repository as historical migration source-of-truth. Treat the current Linux machine as potentially containing newer work that must be preserved. If these conflict, stop and explain the conflict before modifying anything.

## MIGRATION PROVENANCE

These facts were captured from the Windows audit that produced this repository. The future Hermes must preserve them.

- Source audit platform: Windows 11, user `arifi`, project roots `D:\HIGH LEVELS OF WORKS\RedSage_v2` and `D:\HIGH LEVELS OF WORKS\RedSage_v3`, hermes data under `C:\Users\arifi\AppData\Local\hermes\`.
- Migration package: `HERMES_REDSAGE_MIGRATION/` at the repository root.
- Source archive: `D:\HERMES_MIGRATION\HERMES_REDSAGE_MIGRATION.zip` (491,365,160 bytes, SHA-256 `0a2d86afcb185af89e39c215b279342fa06ad306f102d13d76b8d75fead2197c`, 2,810 members).
- Destination repository: `https://github.com/RareBat47/redsage-workflow`.
- Destination branch: `main`.
- Migration commit on remote: `391722bd317bd8d022d4960cc65f85d8c6abf60a`.
- Previous remote HEAD preserved as parent: `54aa7710cc0ad942db28bafefe5275066c96e2a7`.
- Local safety clone during migration: `D:\HERMES_MIGRATION\github_worktree` (no longer needed on Linux).
- Local safety branch during migration: `backup/pre-hermes-redsage-migration` pointing at the previous remote HEAD.
- Git LFS objects (verified on remote):
  - `HERMES_REDSAGE_MIGRATION/RedSage_v2/data/chroma/chroma.sqlite3` — sha256 `196ebe7d755b8fd9731c5481dbbe6c6b54786f27f9ed9f0517d165505adcc507`, 447,475,712 bytes.
  - `HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/chroma/chroma.sqlite3` — sha256 `3e304ae7d9a03a97be7e991025339a403628e5b1ac29bd21e81e6933aac965d6`, 178,507,776 bytes.
- Pre-commit secret-scan report: `HERMES_REDSAGE_MIGRATION/verification/GITHUB_PRECOMMIT_SCAN.json`.
- Sanitization report: `HERMES_REDSAGE_MIGRATION/verification/SANITIZATION_REPORT.json`.
- Final validation report: `HERMES_REDSAGE_MIGRATION/verification/FINAL_VALIDATION.json`.
- Repository visibility at push time: API reported `private: False`. Verify and change visibility on GitHub before relying on this for backup.

## PROCESSES THAT WERE PERFORMED ON WINDOWS

The future Hermes must understand the chain of processes that produced this repository, because some of them (sanitization, exclusion rules) are not derivable from a fresh clone.

1. **Environment audit** of the Windows Hermes install (Hermes Agent v0.21.1 / 2026.9.7, upstream commit `ad03f20d`, Python 3.11.16 venv, default model `anthropic/claude-opus-4.8` via provider `xkiro`).
2. **Approach selection**: Approach C — clean private GitHub migration repository + portable archive, instead of a blind Windows-directory copy.
3. **Package construction** at `D:\HERMES_MIGRATION\HERMES_REDSAGE_MIGRATION\`:
   - `README.md`, `migration/MIGRATION.md`, `migration/MANIFEST.md`, `migration/WINDOWS_TO_LINUX.md`, `SECRETS_REQUIRED.md`, `dependencies/RUNTIME_REQUIREMENTS.md`, `RESTORE_PROMPT.md`, `NEW_HERMES_INITIALIZATION_PROMPT.md` (this file).
   - `mcp/linux/*.sh` (eight Linux launchers) and `mcp/documentation/launcher_conversion.md`.
   - `hermes/config/`, `hermes/memories/`, `hermes/skills/`, `hermes/state/`, `hermes/sessions/` — sanitized portable state.
   - Complete RedSage v2 working tree, complete RedSage v3 working tree, KB/, docs/, RESOURCES/, data/, manifests, receipts, evaluations, and the authorization damage marker.
4. **Sanitization** of the migration copy only — value-free redaction of real high-entropy tokens. Documentation placeholders like `<REDACTED_MIGRATION>`, `$GITHUB_TOKEN`, `os.getenv(...)`, and OWASP cheat-sheet sample names were left intact. Originals on Windows were never modified.
5. **Validation** by `validate_migration_package.py`: required paths present, no `.env`, no `auth.json`, no private keys, no Windows venv/node_modules/caches, no `.exe`, no obvious secret assignments, v2 git status recorded, v3 damage marker present, hermes memories present, hermes skills present, ZIP CRC verified.
6. **Pre-commit secret scan** by `scan_github_commit.py` over the exact worktree files eligible for `git add`. Output stored at `HERMES_REDSAGE_MIGRATION/verification/GITHUB_PRECOMMIT_SCAN.json`. The 21 "hits" were all benign placeholders (verified); no real secret value was committed.
7. **Git LFS** was used for the two Chroma databases. Other source files were tracked normally.
8. **Push** to `https://github.com/RareBat47/redsage-workflow.git` at branch `main`. The previous remote HEAD was not reset; this commit's parent is the previous `main` HEAD.
9. **Remote readback** through the GitHub REST API: commit, NEW_HERMES_INITIALIZATION_PROMPT.md, RESTORE_PROMPT.md, AUTHORIZATION_INDEX_REPAIR_REQUIRED.md, and RedSage_v2.git.bundle were all verified on the remote.

## EXACT EXCLUSION RULES (do not reintroduce)

The future Hermes must respect these exclusion rules. The Windows git staging tree itself was scanned to confirm they were honored.

- Never commit `.env` files containing credentials, `auth.json`, API keys, JWTs, bearer tokens, Telegram bot tokens, GitHub tokens, Cohere / OpenAI / Anthropic / Azure credentials, SSH private keys, certificate/private-key material, browser/session credentials, cookies, active credential databases, Windows credentials, or anything that could authenticate to an external service.
- Never commit `.cmd`, `.exe`, or `.bat` Windows launchers.
- Never commit Windows virtual environments (`.venv`, `.venv_test`, `Scripts/`, `Lib/`, `pyvenv.cfg`, etc.), `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, or similar caches.
- Never commit nested `.git` directories from staged third-party resources, including the temporary ASVS nested pack:

  `RedSage_v3/RESOURCES/.../asvs/.git/objects/pack/tmp_pack_dckse7`

  Their checked-out source/resource content must remain.
- Never commit real high-entropy credential values into source. Sanitize in the migration copy; preserve original evidence on the source platform.

## EXACT INVENTORY COMMITTED TO THE REPOSITORY

```text
NEW_HERMES_INITIALIZATION_PROMPT.md            (root)
.gitattributes                                 (root, LFS pointer config)
HERMES_REDSAGE_MIGRATION/                      (2,746 files)
  README.md
  RESTORE_PROMPT.md
  NEW_HERMES_INITIALIZATION_PROMPT.md          (mirror of root copy)
  SECRETS_REQUIRED.md
  NESTED_GIT_HISTORY.md
  dependencies/
    RUNTIME_REQUIREMENTS.md
    redsage_v2_requirements.txt
    redsage_v3_requirements.txt
    frontend_package.json
    frontend_package-lock.json
    hermes/{.python-version, pyproject.toml, uv.lock, AGENTS.md, README.md, LICENSE}
  mcp/
    documentation/launcher_conversion.md
    linux/{redsage_kb.sh, workflow_kb.sh, assessment_web.sh, evidence_reporting.sh, identity.sh, api.sh, consolidated_roadmap.sh, engagement_workflow.sh}
  migration/{MIGRATION.md, MANIFEST.md, WINDOWS_TO_LINUX.md}
  hermes/
    config/{config.yaml.template, config.yaml.bak-reference}
    memories/{MEMORY.md, USER.md, *.md}
    skills/{autonomous-ai-agents/*, creative/*, email/*, media/*, note-taking/*, productivity/*, research/*, software-development/*, web/*}
    state/{state.db, projects.db, cron/executions.db}
    sessions/{request_dump_*.json}
  RedSage_v2/                                  (full working tree, no nested .git)
  RedSage_v2.git.bundle                        (1,018,053 bytes, portable Git history)
  RedSage_v3/                                  (full working tree, no .git)
  verification/{BUILD_INFO.json, FINAL_VALIDATION.json, GITHUB_PRECOMMIT_SCAN.json, SANITIZATION_REPORT.json, RedSage_v2_git_status.txt, RedSage_v3_git_status.txt, hermes_git_status.txt}
```

## REDSAGE V3 KNOWLEDGE-BASE INVENTORY

The future Hermes must know what KBs are present and which one is damaged.

Six Chroma collections were indexed with model `embed-english-v3.0` (1,024 dimensions):

```text
redsage_v3_workflow_cohere_v1                3,219 vectors  (healthy)
redsage_v3_assessment_web_cohere_v1          2,815 vectors  (healthy)
redsage_v3_evidence_reporting_cohere_v1      2,418 vectors  (healthy)
redsage_v3_assessment_identity_cohere_v1       315 vectors  (healthy)
redsage_v3_assessment_authorization_cohere_v1  183 vectors  (DAMAGED)
redsage_v3_assessment_api_cohere_v1            130 vectors  (healthy)
```

The authorization collection has a corrupt HNSW index (missing `index_metadata.pickle` in its segment directory). Its 183 documents remain in `chroma.sqlite3` but vector queries fail. The damage marker is at:

```text
HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/AUTHORIZATION_INDEX_REPAIR_REQUIRED.md
```

Test count at migration time: **83 passed in ~3.5–4s**. End-to-end engagement evaluation: **6/6 passed** via fresh-subprocess isolation, with results in:

```text
HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/engagement_evaluation_results.json
```

Bounded MCP tools exposed:

```text
search_workflow_kb
search_assessment_web_kb
search_evidence_reporting_kb
search_identity_session_kb
search_api_assessment_kb
assess_evidence_for_draft
generate_internal_roadmap
generate_engagement_workflow
```

Authorization clarification gate is enforced before any provider/vector call when scope is ambiguous. Status `NEEDS_CLARIFICATION`, safety `BLOCKED`, retrieval skipped with reason `authorization_clarification_required`. Findings remain `DRAFT` until evidence and reproduction requirements are met.

## EIGHT MCP SERVERS (LOGICAL NAMES, MUST BE RE-CREATED)

Logical server name, Python module, project root, Linux launcher:

```text
redsage-kb                       RedSage_v2/interfaces/mcp_server.py           $REDSAGE_V2_ROOT      mcp/linux/redsage_kb.sh
redsage-v3-workflow-kb           RedSage_v3/KB/mcp_workflow_server.py          $REDSAGE_V3_ROOT      mcp/linux/workflow_kb.sh
redsage-v3-assessment-web-kb     RedSage_v3/KB/assessment_mcp_server.py        $REDSAGE_V3_ROOT      mcp/linux/assessment_web.sh
redsage-v3-evidence-reporting-kb RedSage_v3/KB/reporting_mcp_server.py         $REDSAGE_V3_ROOT      mcp/linux/evidence_reporting.sh
redsage-v3-identity-kb           RedSage_v3/KB/identity_mcp_server.py          $REDSAGE_V3_ROOT      mcp/linux/identity.sh
redsage-v3-api-kb                RedSage_v3/KB/api_mcp_server.py               $REDSAGE_V3_ROOT      mcp/linux/api.sh
redsage-v3-consolidated-roadmap  RedSage_v3/KB/consolidated_mcp_server.py      $REDSAGE_V3_ROOT      mcp/linux/consolidated_roadmap.sh
redsage-v3-engagement-workflow   RedSage_v3/KB/engagement_mcp_server.py        $REDSAGE_V3_ROOT      mcp/linux/engagement_workflow.sh
```

## DEPENDENCY MANIFESTS (USE THESE EXACTLY)

```text
dependencies/RUNTIME_REQUIREMENTS.md       Hermes Python >=3.11,<3.14; RedSage v2/v3 verified on Python 3.14.7 but verify on target; Node.js for frontend; do not copy Windows venv.
dependencies/redsage_v2_requirements.txt   chromadb>=1.5,<2.0; fastapi>=0.110,<1; uvicorn[standard]>=0.28,<1; pydantic>=2.6,<3; pydantic-settings>=2.2; sqlalchemy>=2.0.28,<3; cohere>=5.3,<6; mcp>=1.2; python-dotenv>=1.0; httpx>=0.27; python-multipart>=0.0.9; pytest>=8; pytest-asyncio>=0.23; pytest-playwright>=0.7.
dependencies/redsage_v3_requirements.txt   chromadb>=1.5,<2.0; fastapi>=0.115; uvicorn>=0.30; mcp>=1.2; python-dotenv>=1.0.
dependencies/hermes/pyproject.toml         Hermes Agent v0.21.1 upstream; uv.lock pinned.
dependencies/hermes/.python-version        3.11
dependencies/hermes/uv.lock                Pinned Hermes dependencies.
dependencies/frontend_package.json         Vite + React lockfile; run `npm ci` in RedSage_v2/frontend.
dependencies/frontend_package-lock.json    Same.
```

## SECRETS REQUIRED ON THE NEW MACHINE

No secret values are included in this repository. Configure them securely through Hermes setup/auth flows or protected environment files. Never print them, never paste them into chat, never commit them.

```text
AZURE_FOUNDRY_API_KEY                Azure Foundry/OpenAI-compatible model access configured by Hermes.
CO_API_KEY                           Cohere embeddings used by RedSage v2/v3 KB build/rebuild.
Local AgentRouter credentials         Only if the local 127.0.0.1:20128/v1 router is retained.
Other model providers                OpenAI, Anthropic, Google, OpenRouter, Kimi, GLM, MiniMax, etc., as selected.
GitHub authentication                For private repository access/pushes.
Telegram bot credentials             Only if Telegram is enabled.
SSH keys/agent credentials           Only if remote access is needed.
OAuth/browser authentication         Must be completed afresh; do not copy cookies or auth databases.
```

## PHASE 0 — FIRST: INSPECT, DO NOT MODIFY

Before doing anything, read the repository in this exact order:

1. `NEW_HERMES_INITIALIZATION_PROMPT.md` (this file)
2. `HERMES_REDSAGE_MIGRATION/RESTORE_PROMPT.md`
3. `HERMES_REDSAGE_MIGRATION/README.md`
4. `HERMES_REDSAGE_MIGRATION/migration/MIGRATION.md`
5. `HERMES_REDSAGE_MIGRATION/migration/MANIFEST.md`
6. `HERMES_REDSAGE_MIGRATION/migration/WINDOWS_TO_LINUX.md`
7. `HERMES_REDSAGE_MIGRATION/SECRETS_REQUIRED.md`
8. `HERMES_REDSAGE_MIGRATION/dependencies/RUNTIME_REQUIREMENTS.md`
9. `HERMES_REDSAGE_MIGRATION/verification/FINAL_VALIDATION.json`
10. `HERMES_REDSAGE_MIGRATION/verification/GITHUB_PRECOMMIT_SCAN.json`
11. `HERMES_REDSAGE_MIGRATION/verification/SANITIZATION_REPORT.json`
12. `HERMES_REDSAGE_MIGRATION/verification/RedSage_v2_git_status.txt`
13. `HERMES_REDSAGE_MIGRATION/hermes/config/`, `hermes/memories/`, `hermes/skills/`, `hermes/state/`, `hermes/sessions/`
14. `HERMES_REDSAGE_MIGRATION/RedSage_v2/.hermes.md`, `AGENTS.md`, `SOUL.md`
15. `HERMES_REDSAGE_MIGRATION/RedSage_v2/docs/internal/HERMES_CONTEXT_SUMMARY.md`, `HERMES_MCP_CONFIG.md`, `KB_COMPLIANCE_NOTES.md`
16. `HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/AUTHORIZATION_INDEX_REPAIR_REQUIRED.md`
17. `HERMES_REDSAGE_MIGRATION/RedSage_v3/docs/KB_BUILD_MASTER_PLAN.md`, `docs/KB_ROADMAP.md`, `docs/KB_IMPLEMENTATION_STATUS.md`
18. `HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/engagement_evaluation_results.json`
19. `HERMES_REDSAGE_MIGRATION/mcp/documentation/launcher_conversion.md`
20. `HERMES_REDSAGE_MIGRATION/mcp/linux/*.sh`
21. `HERMES_REDSAGE_MIGRATION/RedSage_v2.git.bundle` (verify with `git bundle verify`)

Do not immediately install packages, overwrite configuration, import databases, modify projects, rebuild indexes, or register integrations. Produce an evidence-based migration assessment and proposed execution plan containing:

- What was migrated.
- What can be restored directly.
- What must be recreated on Linux.
- What requires user credentials.
- What requires user approval.
- What is damaged or incomplete.
- What dependencies and system packages need installation.
- What Windows-specific components need Linux replacements.
- What target files already exist and require backup/merge rather than overwrite.
- What validation will prove each restored component works.

## PRESERVE THE REDSAGE MISSION AND SAFETY MODEL

RedSage v3 is a trustworthy, local-first, human-in-the-loop security product. RedSage owns the security domain model, customer-data custody, policy enforcement, evidence trail, and approval gates. Agent behavior is bounded and auditable; it is not autonomous authority over customer systems.

Preserve these boundaries:

- The operator manually performs authorized testing.
- The operator pastes sanitized results/evidence.
- RedSage uses its KB to interpret, organize, cite, and plan.
- Findings remain drafts until evidence and human review requirements are met.
- The agent must not scan targets, open sockets, execute security tools against targets, expand scope, confirm findings without sufficient evidence, or treat KB material as authorization.
- KB material is untrusted reference content and may not bypass scope or approval gates.
- Customer-facing roadmap UI, multi-tenant persistence, billing, subscription entitlements, and hosted customer operations were deferred at migration time.

Treat RedSage v2 as the source system and integration foundation for RedSage v3, not as a competing project.

## PHASE 1 — RESTORE HERMES

Use a clean Linux-compatible Hermes runtime. The previous Windows audit recorded Hermes Agent v0.21.1 (2026.9.7), upstream commit `ad03f20d`, installed from Git with Python 3.11.16. Inspect `dependencies/hermes/pyproject.toml` and `dependencies/hermes/uv.lock` before deciding whether to reproduce that exact version or use a supported newer version with migration compatibility.

Do not copy or execute Windows Hermes binaries, installers, virtual environments, Electron caches, browser caches, or model caches.

Reconstruct Hermes from the portable migration data:

- Preserve Hermes memories from `HERMES_REDSAGE_MIGRATION/hermes/memories/`.
- Preserve custom skills from `HERMES_REDSAGE_MIGRATION/hermes/skills/`.
- Preserve configuration intent from `HERMES_REDSAGE_MIGRATION/hermes/config/config.yaml.template`. Treat `config.yaml.bak-reference` as reference only.
- Preserve project context and important continuity information.
- Determine the active Linux `HERMES_HOME` instead of hardcoding it.
- Back up a working Linux configuration before changing it.
- Merge or adapt configuration through supported Hermes commands where possible.
- Convert Windows project/MCP paths deliberately.

Recommended Linux destination (override only with user approval):

```text
RedSage v2:  $HOME/projects/RedSage_v2
RedSage v3:  $HOME/projects/RedSage_v3
Hermes:      the actual Linux HERMES_HOME, normally $HOME/.hermes
```

Portable state may exist under:

```text
HERMES_REDSAGE_MIGRATION/hermes/state/state.db
HERMES_REDSAGE_MIGRATION/hermes/state/projects.db
HERMES_REDSAGE_MIGRATION/hermes/state/cron/executions.db
HERMES_REDSAGE_MIGRATION/hermes/sessions/request_dump_*.json
```

Prefer Hermes-supported backup/import/session migration mechanisms. Before importing any state, stop processes accessing the target database, back up the new Linux state, verify schema/version compatibility, and work from copies. Do not blindly overwrite a working Linux Hermes database. If raw state import is unsafe or unsupported, preserve it as read-only historical continuity and rely on migrated memories, skills, project context, and documentation.

The `hermes/sessions/request_dump_*.json` files were sanitized to redact real high-entropy tokens. They are not raw session exports.

## PHASE 2 — RESTORE REDSAGE V2

Restore the complete packaged working tree from `HERMES_REDSAGE_MIGRATION/RedSage_v2/`. Verify the original Windows Git history through:

```text
git clone HERMES_REDSAGE_MIGRATION/RedSage_v2.git.bundle $HOME/projects/RedSage_v2.upstream.reference
```

The original Windows v2 tree contained local modifications and untracked files not necessarily present in the upstream GitHub history. They are part of the user's working environment and must not be discarded.

Preserve:

- Source code.
- Local modifications and untracked files (compare with `HERMES_REDSAGE_MIGRATION/verification/RedSage_v2_git_status.txt` before changing anything).
- Documentation under `docs/`, `docs/internal/`, `docs/internal/archive/`, `docs/internal/old_runbooks/`, `docs/internal/completed_initiatives/`.
- `.hermes.md`, `AGENTS.md`, `SOUL.md`.
- Hermes context documentation.
- `skills/` and `optional-skills/`.
- Included project data.
- `frontend/package.json` and `frontend/package-lock.json` (use `dependencies/frontend_package*.json` if the in-tree copy is older).

Recreate the Python environment on Linux from `dependencies/redsage_v2_requirements.txt`. Never copy the Windows `.venv` or `.venv_test`. Install frontend dependencies with `npm ci` using the lockfile. Use Linux-compatible scripts (`scripts/dev.sh`, `scripts/build.sh`, `scripts/run.sh`) where available.

The pre-existing `data/redsage.db` and `data/chroma/chroma.sqlite3` are included; verify the Chroma database with `git lfs pull` after cloning.

## PHASE 3 — RESTORE REDSAGE V3

Restore the complete packaged v3 environment from `HERMES_REDSAGE_MIGRATION/RedSage_v3/`. RedSage v3 was not a Git worktree at collection time. Do not infer that any separate Git clone can replace this packaged tree.

Preserve:

- Source.
- `KB/`.
- `docs/`.
- `RESOURCES/` and workflow-generation resources.
- Included data and SQLite databases.
- Chroma persistence data.
- KB build artifacts (`manifests`, `receipts`, `previews`).
- Evaluation cases and results.
- Project documentation and configuration templates.

Recreate its Python environment on Linux from `dependencies/redsage_v3_requirements.txt`. Do not copy Windows virtual environments.

## PHASE 4 — LINUX ADAPTATION

Search the migrated safe configuration and project trees for Windows-specific dependencies, including:

- `C:\...` and `C:/...` paths.
- `D:\...` and `D:/...` paths.
- The Windows username `arifi` where used as an active path.
- `.cmd` launchers.
- `.exe` commands.
- PowerShell-specific commands.
- Windows Python environments and `Scripts/python` paths.
- Windows-only filesystem assumptions, path separators, services, and shell behavior.

Do not perform blind global string replacements. Classify each occurrence as active configuration, historical evidence, documentation, test fixture, Git record, migration receipt, or runtime launcher. Preserve historical records while adapting active paths.

Do not change application behavior unnecessarily merely to make paths work. Preserve behavior first; improve later.

## PHASE 5 — MCP

Recreate all eight required logical MCP integrations from the provided Linux material. Do not copy or run old Windows `.cmd` launchers. Inspect `HERMES_REDSAGE_MIGRATION/mcp/documentation/launcher_conversion.md` and the eight scripts under `HERMES_REDSAGE_MIGRATION/mcp/linux/`. Use those scripts or direct Linux Python module commands after adapting project/interpreter variables.

Set environment variables before each launch:

```text
REDSAGE_V2_ROOT=$HOME/projects/RedSage_v2
REDSAGE_V3_ROOT=$HOME/projects/RedSage_v3
PYTHON_BIN=python3
```

Verify every MCP server individually in layers:

1. Python module import.
2. Direct server startup/smoke test.
3. MCP handshake and tool discovery.
4. Hermes registration using the exact logical server name.
5. Hermes MCP connection test.
6. Live bounded tool call.
7. Citation and receipt readback.
8. Safety-state verification.

Never invent credentials or fabricate successful connections. Do not expose raw database access, unrestricted filesystem access, index mutation, workflow mutation, scope approval, or finding confirmation through MCP.

## PHASE 6 — CREDENTIALS

Use `HERMES_REDSAGE_MIGRATION/SECRETS_REQUIRED.md` as the authoritative list of credential types. Credentials are intentionally absent.

Ask the user for secure configuration only when a credential is actually necessary. Never ask the user to paste a password, token, API key, card number, or verification code into ordinary chat if Hermes provides a secure vault or masked setup mechanism.

Never print credentials into logs, source files, Git commits, reports, terminal commands, screenshots, or chat. Never search session history, request dumps, caches, or project evidence to recover excluded credentials.

Configure credentials through an appropriate secret manager, Hermes secure setup/auth flow, or protected environment files that remain Git-ignored. Verify that a credential exists and works without printing its value.

The AgentRouter is a machine-level service and is not recreated by copying Hermes configuration. Inspect whether it must be installed, recreated, replaced, or removed from the active provider chain.

## PHASE 7 — REDSAGE V3 DAMAGE

Pay special attention to:

```text
HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/AUTHORIZATION_INDEX_REPAIR_REQUIRED.md
```

The migration explicitly identifies `redsage_v3_assessment_authorization_cohere_v1` as damaged. Its 183 document/metadata rows were present at migration time, but Chroma vector queries failed with an internal HNSW segment-reader error.

Do not claim it is healthy. Do not automatically rebuild it or consume Cohere credits.

First explain to the user:

- What is damaged.
- What depends on it.
- Whether the rest of RedSage works without it.
- What rebuilding requires.
- The expected resource/API implications.
- How an isolated versioned rebuild and rollback would work.

Before repair, preserve the migrated damaged state, inspect its preview manifest and receipts, verify the other collections independently, and confirm Chroma/embedding-model compatibility. Wait for approval before any paid re-embedding. Build a replacement collection rather than silently mutating a published one. Verify count, metadata, retrieval, citations, receipts, and evaluations before switching the active profile.

## PHASE 8 — VALIDATION

Do not declare anything working because files merely exist. Run safe, relevant checks and preserve actual outputs.

### Hermes

Verify:

- Hermes starts correctly.
- The intended `HERMES_HOME` is active.
- Configuration loads without Windows-path errors.
- Memories are available.
- Skills are discoverable.
- Required tools work.
- At least one configured model provider completes a bounded real request.
- Imported session/state data, if any, passes compatibility and integrity checks.
- No Windows executable or launcher is active.

### RedSage v2

Verify:

- Fresh Linux Python environment works.
- Required package imports work.
- Included databases are readable.
- Backend starts and responds to a health/smoke request.
- Tests run under the recreated environment.
- Frontend dependencies install from the lockfile.
- Frontend builds.
- Local modifications and untracked files remain preserved relative to `verification/RedSage_v2_git_status.txt`, except for reviewed Linux adaptations.
- `redsage-kb` MCP starts, is discovered, and handles a bounded request.

### RedSage v3

Verify:

- Fresh Linux Python environment works.
- Required package imports work.
- SQLite databases are readable.
- KB and workflow resources are present.
- Build manifests and receipts are readable.
- Every expected Chroma collection is inspected and queried independently.
- Healthy collections return live retrieval results.
- The authorization collection remains marked damaged until rebuilt and validated.
- Every v3 MCP server starts and is discovered.
- Consolidated retrieval and roadmap generation work with available healthy collections.
- Citations and retrieval receipts are generated.
- Authorization and safety gates remain fail-closed.
- The engagement workflow never executes security actions or confirms findings automatically.
- Evaluation suites run and actual results are reported.

### Integrations

Verify only when configured:

- Azure/model-provider connectivity.
- Cohere connectivity.
- Local AgentRouter or replacement service.
- MCP discovery and live bounded calls.
- Telegram.
- GitHub authentication and remote access.
- SSH.
- Browser authentication.

## PHASE 9 — FINAL REPORT

At completion, produce a concise but complete migration report with these exact sections:

### RESTORED

List files, state, projects, memories, skills, and integrations successfully restored.

### RECREATED

List Linux runtimes, virtual environments, dependencies, launchers, and services recreated.

### REQUIRES CREDENTIALS

List missing credential types and integrations without exposing values.

### REQUIRES USER APPROVAL

List pending actions requiring approval, especially paid API use, damaged-index repair, data replacement, or architectural changes.

### FAILED

List actual failed validations and relevant evidence.

### DAMAGED

List known or newly discovered damaged data, including the authorization Chroma collection.

### NOT TESTED

List components that could not be tested and why.

### REMAINING ACTIONS

List ordered next steps, owners, and blockers.

Also report files/configuration intentionally not restored, MCP servers verified, exact test commands and counts, database-integrity results, Linux adaptations made, rollback locations, and deliberate deviations from the migration manifest.

## IMPORTANT BEHAVIOR

Do not destroy existing work.

Never:

- Delete migration files because they appear unnecessary.
- Overwrite a working configuration without first backing it up.
- Delete or replace current Linux project work without comparison and approval.
- Reset Git repositories without approval.
- Run `git clean`, destructive checkout, or hard reset unnecessarily.
- Discard untracked files or local modifications.
- Overwrite databases without backups.
- Rebuild or mutate published indexes in place.
- Consume Cohere credits without approval.
- Silently resolve ambiguity by guessing.
- Fabricate successful tests, provider calls, MCP connections, or data integrity.

If two sources disagree, stop and explain the exact conflict. Treat this repository as the historical migration source of truth, while preserving potentially newer Linux work. Migration comes first. Improvement comes later. Preserve behavior before optimizing.

Only declare migration success after all stated acceptance criteria have real verification evidence.

## KNOWN GAPS / FOLLOW-UPS

- Repository visibility was `private: False` at push time. If the user wanted the repository private, this must be changed in GitHub settings. The future Hermes must confirm and not assume privacy.
- Authorization KB repair is still pending and requires Cohere credits plus explicit user approval.
- Hermes session DBs were included as portable copies; their import depends on the target Hermes version. Test before relying on them.
- The two `.cmd` Windows launchers from the user's `C:\Users\arifi\` were intentionally not migrated. Re-create them on Linux if needed using the equivalents in `mcp/linux/*.sh`.
- Git LFS must be installed on the target Linux machine before `git lfs pull` can fetch the two Chroma databases.
