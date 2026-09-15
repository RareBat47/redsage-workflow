# skill_db_migration_idempotent — Add a safe SQLite migration

## Purpose
Add one idempotent RedSage SQLite schema change using the repository’s `init_db` migration pattern.

## When to use
- A ticket requires a new column, table, index, relationship, or compatible schema evolution.

## Procedure
1. Read `AGENTS.md`, current models, database initialization, migration checks, and archive import/export code.
   - Completion: document the fresh-database and existing-database paths.
2. Obtain explicit confirmation for schema changes unless the operator explicitly requested the migration.
   - Completion: approval covers the proposed schema and files.
3. Implement the migration with reflection/introspection plus conditional DDL, matching current `init_db` conventions.
   - Completion: rerunning initialization does not fail or duplicate schema changes.
4. Update models, schemas, routes/services, export/import remapping, and docs only where required by the changed entity.
   - Completion: archive behavior preserves the new data without secrets, zip-slip risk, or cross-project leakage.
5. Add tests for fresh DB, legacy DB, idempotent repeat initialization, and affected archive behavior.
   - Completion: tests use temporary databases and cover a real migration path.
6. Run compile, non-E2E tests, frontend build if contracts changed, and append the receipt to `docs/internal/PROGRESS.md`.
   - Completion: all gate outcomes are real and recorded.

## Guardrails
Never run raw destructive schema changes without confirmation. Never modify `core/**` or `data/chroma/**`. Preserve scope, evidence, audit, and archive integrity rules.

## Output
Schema delta, migration safety proof, tests/gates, affected export/import behavior, and rollback path.
