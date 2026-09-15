# skill_add_api_endpoint — Add one safe API endpoint

## Purpose
Add one validated RedSage endpoint with focused tests and documentation.

## When to use
- A ticket explicitly requests a backend API route.

## Procedure
1. Read `AGENTS.md`, existing router/schema patterns, and the OpenAPI route set.
   - Completion: identify the router, request/response schemas, auth/scope gates, and persistence path.
2. Confirm the endpoint does not execute tools, scan targets, generate payloads, or bypass scope locks.
   - Completion: unsafe behavior is rejected or redesigned as display-only workflow support.
3. Add schema validation, route logic, audit events, and persistence using existing patterns.
   - Completion: malformed, unauthorized, out-of-scope, and missing-resource paths return the established errors.
4. Add focused tests for success and safety boundaries.
   - Completion: tests assert behavior, not source text.
5. Update `EXPLANATION.md` and `docs/USER_MANUAL.md` when behavior is user-visible.
   - Completion: docs describe the actual route and limitations.
6. Run the compile, non-E2E test, and frontend build gates when applicable; append results to `docs/internal/PROGRESS.md`.
   - Completion: every named gate has a real exit result.

## Guardrails
Never modify `core/**` or `data/chroma/**`. Evidence is untrusted and must be clipped/redacted before AI use. Confirm before schema changes or other state-changing work.

## Output
Changed files, route behavior, safety checks, tests, gates, and rollback path.
