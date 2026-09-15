# skill_archive_export_import_update — Extend portable archives

## Purpose
Safely extend RedSage single-project export/import for a new entity or field.

## When to use
- A change adds persisted data that must survive a project archive round trip.

## Procedure
1. Read `AGENTS.md`, archive export/import services, schema relationships, and existing archive tests.
   - Completion: identify all IDs that need remapping and all links that must remain project-scoped.
2. Confirm the archive stays single-project and excludes `.env`, keys, unrelated projects, and raw files outside the selected project.
   - Completion: input/output boundaries are explicit.
3. Extend export with checksums and deterministic manifest handling using existing patterns.
   - Completion: no untracked secrets or unrelated content are included.
4. Extend import with zip-slip validation, ID remapping, parent-child ordering, and rollback on any failure.
   - Completion: a failed import leaves no partial project state.
5. Add round-trip, legacy-archive compatibility, invalid-checksum, zip-slip, remapping, and rollback tests as applicable.
   - Completion: tests prove the changed entity survives with correct parent IDs.
6. Run compile, non-E2E tests, and frontend build if user-visible behavior changed. Append results to `docs/internal/PROGRESS.md`.
   - Completion: release receipt reflects the verified paths.

## Guardrails
Confirm before schema or product-code changes unless explicitly requested. Never modify `core/**` or `data/chroma/**`. Never weaken integrity checks to accommodate malformed input.

## Output
Archive format delta, compatibility statement, test/gate results, and rollback note.
