# skill_ticket_execute_incremental — Deliver one bounded change

## Purpose
Implement one approved RedSage ticket in the smallest safe increment, with tests, documentation, gates, and a rollback note.

## When to use
- The operator has named a concrete ticket or acceptance criteria.
- Do not use for exploratory work or a request spanning unrelated milestones.

## Procedure
1. Re-read `SOUL.md`, `AGENTS.md`, this ticket, and `docs/internal/PROGRESS.md`.
   - Completion: state the acceptance criteria, allowed files, and forbidden zones.
2. Inspect the existing behavior and tests before editing.
   - Completion: identify the narrowest implementation and test locations.
3. If the change touches code, schema, dependencies, or files outside the documentation/skill zones, obtain explicit confirmation unless the operator already requested that change.
   - Completion: approval scope matches the planned files.
4. Make the minimal implementation. Never modify `core/**` or `data/chroma/**`.
   - Completion: no unrelated formatting, refactors, or generated artifacts.
5. Add or update focused tests. Preserve RedSage safety rules: no execution/scanning automation, no payload generation, scope-lock gates, redaction before AI use, and archive integrity.
   - Completion: tests cover the acceptance criteria and relevant failure path.
6. Update ground-truth docs when observable behavior changes.
   - Completion: `EXPLANATION.md` and operator documentation match the implementation, when present.
7. Run `.venv/Scripts/python.exe -m compileall backend`, `.venv/Scripts/python.exe -m pytest -m "not e2e"`, and `npm run build` from `frontend/` when applicable.
   - Completion: record exact results; stop at the first blocking gate failure.
8. Append a dated receipt to `docs/internal/PROGRESS.md`.
   - Completion: include files changed, tests/gates, rollback note, and next step.

## Rollback note
Record the smallest rollback: revert the named implementation and test/doc files together. Do not commit or push without explicit instruction.

## Output
Report changed files, safety impact, test/gate results, and rollback path. Never fabricate a passing result.
