# skill_frontend_flow_change — Change a UI flow safely

## Purpose
Implement one RedSage frontend flow change while preserving the state-based view architecture and safety posture.

## When to use
- A ticket changes a React/Vite interaction, panel, form, or workflow view.

## Procedure
1. Read `AGENTS.md`, `frontend/src/main.tsx`, related components/types/styles, and existing tests.
   - Completion: identify the state owner and existing interaction pattern; do not introduce a router unless the repository already uses one.
2. Confirm the UI only supports display-only commands and human-operated workflow actions.
   - Completion: no direct tool execution, scanning, payload generation, or scope bypass is introduced.
3. Make the smallest component/type/style change.
   - Completion: loading, error, disabled, and empty states remain explicit where relevant.
4. Add focused API-contract or UI behavior coverage using the project’s existing approach.
   - Completion: success and rejection behavior are covered.
5. Run `npm run build` from `frontend/`, plus backend compile/non-E2E tests if a shared contract changed.
   - Completion: report exact results and any existing warnings separately.
6. Update user-facing docs when flow behavior changes and append the result to `docs/internal/PROGRESS.md`.
   - Completion: docs and progress receipt name all modified files.

## Guardrails
Never modify `core/**` or `data/chroma/**`. Confirm before product code changes unless explicitly requested. Do not hide unsafe operations behind the UI.

## Output
Changed flow, files, safety impact, tests/build, and rollback path.
