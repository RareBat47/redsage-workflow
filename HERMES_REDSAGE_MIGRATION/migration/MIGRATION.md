# Migration procedure

When restoring from the private Git repository, `../NEW_HERMES_INITIALIZATION_PROMPT.md` is the first instruction and `../RESTORE_PROMPT.md` is the authoritative package-level restore contract. When restoring from the standalone ZIP, begin with `../RESTORE_PROMPT.md`. Require the fresh Linux Hermes agent to complete the inspection-first assessment before modifying the new environment.

1. On a fresh Linux VM, install Hermes using its current official Linux installer. Do not copy the Windows Hermes executable or virtual environment.
2. Before changes, read `RESTORE_PROMPT.md`, `migration/MANIFEST.md`, `migration/MIGRATION.md`, `migration/WINDOWS_TO_LINUX.md`, and `SECRETS_REQUIRED.md`, resolving these paths from the extracted package root.
3. Choose destination paths, preferably `$HOME/projects/RedSage_v2`, `$HOME/projects/RedSage_v3`, and `$HOME/.hermes`; do not overwrite an existing installation without a backup.
4. Restore the RedSage_v2 and RedSage_v3 trees from this package. Preserve the included v2 `.git` history and local/untracked files.
5. Create fresh Linux Python environments. Use Hermes requirements/lock metadata, then each RedSage `requirements.txt`. Do not copy Windows environments.
6. Run `npm ci` in `RedSage_v2/frontend`; do not copy node_modules.
7. Restore memories and reviewed skills into the target Hermes home. Adapt the sanitized config template and register Linux MCP scripts using the logical server names.
8. Configure required secrets securely according to `SECRETS_REQUIRED.md`; do not search for or fabricate values. Recreate or replace the local AgentRouter service if required.
9. Restore Hermes state/session databases only through Hermes-supported import/restore where available. If using the included SQLite snapshots, stop Hermes first, back up the target DB, and verify compatibility; do not blindly overwrite.
10. Run project tests, database checks, MCP discovery, and live bounded calls. Verify the authorization collection remains marked damaged until rebuilt and validated.
11. Only after verification should the new environment be considered operational.
