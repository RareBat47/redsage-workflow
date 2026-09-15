# Migration manifest

| Included component | Original Windows path | Linux destination | Status | Notes |
|---|---|---|---|---|
| Git-clone initialization prompt | newly generated migration instruction | package root `NEW_HERMES_INITIALIZATION_PROMPT.md` | generated | first file a brand-new Hermes reads after cloning the private repository |
| Authoritative restore prompt | newly generated migration instruction | package root `RESTORE_PROMPT.md` | generated | package-level restoration contract read immediately after initialization prompt |
| Hermes config template | `C:\Users\arifi\AppData\Local\hermes\config.yaml` | `$HERMES_HOME/config.yaml` | copied/sanitized | Windows paths converted to variables; inspect before use |
| Hermes memories | `...\hermes\memories` | `$HERMES_HOME/memories` | copied | portable context |
| Hermes skills | `...\hermes\skills` | `$HERMES_HOME/skills` | copied | reviewed for secrets before packaging |
| Hermes state snapshots | `...\hermes\state.db`, `projects.db` | `$HERMES_HOME/*.db` | SQLite backup snapshots | use supported import or restore only with backup |
| Hermes sessions | `...\hermes\sessions` | `$HERMES_HOME/sessions` | copied | sensitive continuity data |
| Hermes cron | `...\hermes\cron` | `$HERMES_HOME/cron` | copied | recreate/verify scheduler |
| RedSage v2 | `D:\HIGH LEVELS OF WORKS\RedSage_v2` | `$HOME/projects/RedSage_v2` | copied/filtered | local modifications, untracked files, `.git` included; venv/node_modules excluded |
| RedSage v3 | `D:\HIGH LEVELS OF WORKS\RedSage_v3` | `$HOME/projects/RedSage_v3` | copied/filtered | KB, docs, resources, data and artifacts included; `.env` excluded |
| v2 Git record | RedSage_v2 `.git` | same relative location | copied | see `verification/RedSage_v2_git_status.txt` |
| v3 Git record | no repository | N/A | recorded | v3 was not a Git worktree at audit time |
| Linux MCP launchers | Windows `C:\Users\arifi\redsage-v3-*.cmd` | `mcp/linux/*.sh` | rebuilt | direct `python -m` modules with Linux variables |
| Dependencies | Hermes `pyproject.toml`/`uv.lock`, v2/v3 requirements, frontend locks | `dependencies/` | copied manifests | recreate runtimes; no environments copied |
| Damage marker | v3 auth collection | v3 `data/kb_build/` | documented | authorization index requires repair/rebuild |

Excluded intentionally: all `.env` files, Hermes `auth.json`, virtual environments, `node_modules`, `.exe`, caches, temporary files, lock files, browser/Electron state, and private keys.

The archive is a reconstruction package, not a byte-for-byte Windows clone.
