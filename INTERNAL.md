# Internal Docs & Devtools

Development-phase material lives outside the runtime path. Nothing below is
required to run, test, or build RedSage v2.

## Where things moved

- `docs/internal/PROGRESS.md` — milestone-by-milestone build history and test logs
- `docs/internal/AI_BENCHMARK_REPORT.md` — live Cohere benchmark results
- `docs/internal/old_runbooks/` — original one-day build runbook, Day-2/Day-3
  implementation plans, early planning notes, and pre-live test checklist
- `devtools/migrations/migrate_day2.py` — one-shot SQLite migration (already
  executed; kept for history)
- `devtools/diagnostics/inspect_db.py` — ad-hoc database inspection helper

## Notes

- The app never imports anything from `docs/internal/` or `devtools/`.
- The opt-in live benchmark test (`pytest tests/test_live_ai_benchmark.py -v -s`)
  writes its report to `docs/internal/AI_BENCHMARK_REPORT.md` and updates
  `docs/internal/PROGRESS.md`.
- For a clean explorer view during manual testing, open
  `HUMAN_TESTING.code-workspace`, which hides these folders plus generated
  project data (`data/projects/**`, `data/redsage.db`).
- System documentation for the current build: `EXPLANATION.md` (root) and
  `README.md`, `docs/RUN.md`, `docs/DEMO.md`, `docs/SECURITY.md`,
  `docs/ARCHIVE_FORMAT.md`.
