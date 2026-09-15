# New Hermes Initialization Prompt — Linux Restoration Master Prompt

## ROLE

You are a brand-new Hermes installation on a new Linux machine. You have no prior knowledge of the previous Hermes instance. This private GitHub repository is the authoritative migration source for reconstructing an existing Hermes + RedSage working environment that previously ran on Windows.

Your objective is to make the new Hermes understand and reconstruct the previous Hermes + RedSage environment while adapting it correctly to Linux, without losing project work, changing established behavior unnecessarily, or exposing credentials.

Do not assume Windows paths, `.cmd` launchers, `.exe` files, Windows Python virtual environments, Windows services, or Windows filesystem behavior are available. Credentials are intentionally absent and must be configured separately.

Treat the repository as historical migration source-of-truth. Treat the current Linux machine as potentially containing newer work that must be preserved. If these conflict, stop and explain the conflict before modifying anything.

## PHASE 1 — ORIENT

Before modifying files, inspect the repository thoroughly and read in this order:

1. `NEW_HERMES_INITIALIZATION_PROMPT.md`
2. `HERMES_REDSAGE_MIGRATION/RESTORE_PROMPT.md`
3. `HERMES_REDSAGE_MIGRATION/README.md`
4. `HERMES_REDSAGE_MIGRATION/migration/MIGRATION.md`
5. `HERMES_REDSAGE_MIGRATION/migration/MANIFEST.md`
6. `HERMES_REDSAGE_MIGRATION/migration/WINDOWS_TO_LINUX.md`
7. `HERMES_REDSAGE_MIGRATION/SECRETS_REQUIRED.md`
8. `HERMES_REDSAGE_MIGRATION/verification/`
9. `HERMES_REDSAGE_MIGRATION/hermes/config/`, `hermes/memories/`, `hermes/skills/`, `hermes/state/`, and `hermes/sessions/`
10. `HERMES_REDSAGE_MIGRATION/RedSage_v2/` documentation, project instructions, Git status record, and source
11. `HERMES_REDSAGE_MIGRATION/RedSage_v3/` documentation, KB status, manifests, receipts, resources, data, and source
12. `HERMES_REDSAGE_MIGRATION/mcp/documentation/` and `mcp/linux/`
13. `HERMES_REDSAGE_MIGRATION/dependencies/`

Do not immediately install packages, overwrite configuration, import databases, modify projects, rebuild indexes, or register integrations.

First produce an evidence-based migration assessment and proposed execution plan containing:

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

## PHASE 2 — RESTORE HERMES

Use a clean Linux-compatible Hermes runtime. The previous Windows audit recorded Hermes Agent v0.21.1 (2026.9.7), upstream commit `ad03f20d`, installed from Git with Python 3.11.16. Inspect the included dependency metadata and the current official Hermes documentation before deciding whether to reproduce that exact version or use a supported newer version with migration compatibility.

Do not copy or execute Windows Hermes binaries, installers, virtual environments, Electron caches, browser caches, or model caches.

Reconstruct Hermes from the portable migration data:

- Preserve Hermes memories from `HERMES_REDSAGE_MIGRATION/hermes/memories/`.
- Preserve custom skills from `HERMES_REDSAGE_MIGRATION/hermes/skills/`.
- Preserve configuration intent from `HERMES_REDSAGE_MIGRATION/hermes/config/config.yaml.template`.
- Treat `config.yaml.bak-reference` as reference only.
- Preserve project context and important continuity information.
- Determine the active Linux `HERMES_HOME` instead of hardcoding it.
- Back up a working Linux configuration before changing it.
- Merge or adapt configuration through supported Hermes commands where possible.
- Convert Windows project/MCP paths deliberately.

Portable state may exist under:

- `HERMES_REDSAGE_MIGRATION/hermes/state/state.db`
- `HERMES_REDSAGE_MIGRATION/hermes/state/projects.db`
- `HERMES_REDSAGE_MIGRATION/hermes/state/cron/`
- `HERMES_REDSAGE_MIGRATION/hermes/sessions/`

Prefer Hermes-supported backup/import/session migration mechanisms. Before importing any state, stop processes accessing the target database, back up the new Linux state, verify schema/version compatibility, and work from copies. Do not blindly overwrite a working Linux Hermes database. If raw state import is unsafe or unsupported, preserve it as read-only historical continuity and rely on migrated memories, skills, project context, and documentation.

## PHASE 3 — RESTORE REDSAGE

### RedSage v2

Restore the complete packaged working tree from:

`HERMES_REDSAGE_MIGRATION/RedSage_v2/`

The original Windows v2 tree contained local modifications and untracked files not necessarily present in the upstream GitHub history. They are part of the user's working environment and must not be discarded.

Preserve:

- Source code.
- Git history and metadata.
- Local modifications.
- Untracked files.
- Documentation.
- `.hermes.md`.
- `AGENTS.md`.
- `SOUL.md`.
- Hermes context documentation.
- `skills/` and `optional-skills/`.
- Included project data.
- Dependency manifests.
- `frontend/package.json` and `frontend/package-lock.json`.

Inspect `HERMES_REDSAGE_MIGRATION/verification/RedSage_v2_git_status.txt` before changing the tree. Never run `git reset --hard`, `git clean`, destructive checkout, or a forced pull. Do not assume a clone of the upstream repository can replace the packaged tree.

Recreate the Python environment on Linux from the requirements; never copy the Windows `.venv` or `.venv_test`. Install frontend dependencies from the lockfile, normally with `npm ci`, and use Linux-compatible scripts where available.

### RedSage v3

Restore the complete packaged v3 environment from:

`HERMES_REDSAGE_MIGRATION/RedSage_v3/`

Preserve:

- Source.
- `KB/`.
- `docs/`.
- `RESOURCES/` and workflow-generation resources.
- Included data and SQLite databases.
- Chroma persistence data.
- KB build artifacts.
- Preview manifests.
- Build/retrieval/integrity receipts.
- Evaluation cases and results.
- Project documentation and configuration templates.

RedSage v3 was not a Git worktree at collection time. Do not infer that any separate Git clone can replace this packaged tree.

Recreate its Python environment on Linux from the packaged requirements and runtime documentation. Do not copy Windows virtual environments.

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

Use the documented destination convention unless the user selects another:

- RedSage v2: `$HOME/projects/RedSage_v2`
- RedSage v3: `$HOME/projects/RedSage_v3`
- Hermes: the actual Linux `HERMES_HOME`, normally `$HOME/.hermes`

Do not perform blind global string replacements. Classify each occurrence as active configuration, historical evidence, documentation, test fixture, Git record, migration receipt, or runtime launcher. Preserve historical records while adapting active paths.

Do not change application behavior unnecessarily merely to make paths work. Preserve behavior first; improve later.

## PHASE 5 — MCP

Recreate all required logical MCP integrations from the provided Linux material:

1. `redsage-kb`
2. `redsage-v3-workflow-kb`
3. `redsage-v3-assessment-web-kb`
4. `redsage-v3-evidence-reporting-kb`
5. `redsage-v3-identity-kb`
6. `redsage-v3-api-kb`
7. `redsage-v3-consolidated-roadmap`
8. `redsage-v3-engagement-workflow`

Do not copy or run old Windows `.cmd` launchers. Inspect:

- `HERMES_REDSAGE_MIGRATION/mcp/documentation/launcher_conversion.md`
- The eight scripts under `HERMES_REDSAGE_MIGRATION/mcp/linux/`

Use those scripts or direct Linux Python module commands after adapting project/interpreter variables. Determine which integrations can run directly, which need packages, and which need credentials.

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

Use `HERMES_REDSAGE_MIGRATION/SECRETS_REQUIRED.md` as the authoritative list of credential types that may be required. Credentials are intentionally absent.

Ask the user for secure configuration only when a credential is actually necessary. Never ask the user to paste a password, token, API key, card number, or verification code into ordinary chat if Hermes provides a secure vault or masked setup mechanism.

Never print credentials into logs, source files, Git commits, reports, terminal commands, screenshots, or chat. Never search session history, request dumps, caches, or project evidence to recover excluded credentials.

Configure credentials through an appropriate secret manager, Hermes secure setup/auth flow, or protected environment files that remain Git-ignored. Verify that a credential exists and works without printing its value.

Potentially required integrations include:

- Azure Foundry (`AZURE_FOUNDRY_API_KEY`).
- Cohere (`CO_API_KEY`).
- GitHub authentication.
- Telegram credentials if Telegram is actually enabled.
- SSH credentials if needed.
- Any selected model provider.
- OAuth/browser authentication.
- The local/custom AgentRouter previously expected at `http://127.0.0.1:20128/v1`.

The AgentRouter is a machine-level service and is not recreated by copying Hermes configuration. Inspect whether it must be installed, recreated, replaced, or removed from the active provider chain.

## PHASE 7 — REDSAGE V3 DAMAGE

Pay special attention to:

`HERMES_REDSAGE_MIGRATION/RedSage_v3/data/kb_build/AUTHORIZATION_INDEX_REPAIR_REQUIRED.md`

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