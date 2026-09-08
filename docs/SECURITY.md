# RedSage v2: Security Model

RedSage v2 is a local-first, single-operator, human-in-the-loop penetration
testing and audit workflow companion. It does **not** execute security tooling,
launch scans, open sockets to targets, or automate attacks. The application
records evidence that the operator collects manually.

## Scope enforcement

- Every project has a `scopes` row with a whitelist, blacklist, rate limit, and
  lock state.
- Evidence verification is blocked while a project's scope is unlocked.
- Suggested command templates resolve `{target_host}` from the whitelist and
  expose the command as copyable only when the resolved host is in-scope and
  the scope is locked.
- Scope amendments require additional targets that pass strict validation, a
  non-empty authorizing entity, a rationale of at least 10 characters, and are
  recorded permanently in `scope_amendments` and `audit_events`.

These controls are documentation and workflow guards. They are not a
substitute for legal authorization or network-level controls.

## Redaction of sensitive data

- Evidence pasted by the operator is clipped to a bounded number of lines and
  regex-redacted **in memory** before any AI call.
- Redaction patterns remove bearer tokens, passwords/passphrases assigned with
  `=`, and JWT-shaped strings.
- The database stores only a `redacted_excerpt` (first ~800 characters of the
  already-redacted text) plus metadata — never the full raw evidence. Full raw
  evidence lives only on disk under `data/projects/{project_id}/artifacts/`.
- AI prompts wrap sanitized evidence in an `<untrusted_evidence_log>` boundary
  and require JSON-only structured output. Contents inside that boundary are
  treated as inert data, never as instructions.

## Untrusted evidence handling

- Pasted logs are treated as untrusted target output.
- Evidence is clipped, redacted, XML-bounded, and JSON-schema validated before
  being sent to Cohere.
- When no Cohere key is configured, verification runs fully offline with a
  deterministic local verifier; no evidence leaves the machine.

## Offline mode

- With `CO_API_KEY` unset (or `COHERE_API_KEY`), all workflow, evidence,
  reporting, export, and import features run without any outbound call.
- Only the optional Cohere verification/suggestion features require a key and
  an outbound call. The public distribution does not include the knowledge-base
  engine (`core/`) or its vector store (`data/chroma/`); the workflow
  application itself never requires a key.

## Export/import integrity

- Project archives are created locally by the backend as a single ZIP.
- Archives contain only the selected project's JSON rows, its evidence
  artifact files, a generated report snapshot, and a `manifest.json`.
- `.env`, API keys, and external configuration are never exported.
- Import validates `manifest.json` format, member paths (zip-slip and absolute
  path rejection), member count/size caps, and SHA-256 checksums before any
  data is written.
- Imported projects always receive a new project ID with all row and foreign
  keys remapped; existing projects are never overwritten.
- Failed imports roll back and remove only the newly created project directory.

See `docs/ARCHIVE_FORMAT.md` for the full layout and limits.

## Local data boundaries

- The database is a local SQLite file (`data/redsage.db`).
- Artifacts live under `data/projects/`.
- This public distribution excludes the preserved knowledge base
  (`core/`, `data/chroma/`); the application does not depend on it.
- Bind servers to `127.0.0.1` in local mode; do not expose the service to
  untrusted networks.

## Operator responsibility

Use RedSage only for systems covered by explicit written authorization that
matches the locked project scope. Never submit client secrets, credentials, or
unrelated sensitive datasets to the AI service.
