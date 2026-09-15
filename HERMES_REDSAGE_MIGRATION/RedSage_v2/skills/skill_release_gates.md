# skill_release_gates — Release-readiness gate

## Purpose
Run the RedSage v2 quality gates and produce a deterministic GO/NO-GO report. Do not implement fixes as part of this skill.

## When to use
- Before a demo or merge.
- After an executable code, schema, or configuration change.
- Do not use for E2E unless the operator explicitly requests it.

## Preconditions
- Work from the repository root.
- Re-read `AGENTS.md` and confirm `core/**` and `data/chroma/**` are forbidden edit zones.
- Use `.venv/Scripts/python.exe`; do not substitute an ambient interpreter.

## Procedure
1. Capture `git status --short`.
   - Completion: the report identifies whether the tree contains changes.
2. Run `.venv/Scripts/python.exe -m compileall backend`.
   - Completion: exit code is zero. On failure, stop and report the first error.
3. Run `.venv/Scripts/python.exe -m pytest -m "not e2e"`.
   - Completion: exit code is zero. On failure, classify the failure as regression, flaky, or environment dependency; stop before frontend build.
4. Run `npm run build` from `frontend/`.
   - Completion: exit code is zero. Record warnings separately from failures.
5. Run E2E only when explicitly requested and a server is confirmed on `127.0.0.1:8000`.
   - Completion: report the E2E result or `E2E skipped: explicit-request policy` / `server not running`.
6. Append the short receipt to `docs/internal/PROGRESS.md`.
   - Completion: include timestamp, exact commands, short results, and recommended next step.

## Failure handling
- Do not claim a gate passed when its command could not run.
- For interpreter/dependency failures, propose: use the project venv, install dependencies only with approval, or correct the working directory.
- Never change unrelated code to make a different gate pass.

## Output
Use this exact structure:

```text
Summary: GO | NO-GO
Compile: PASS | FAIL
Tests: PASS | FAIL
Frontend build: PASS | FAIL
E2E: PASS | FAIL | SKIPPED
Risks: <up to three items>
Next actions: <one to five bullets>
```
