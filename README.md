# RedSage v2

Local-first, single-operator, **human-in-the-loop** security assessment and
audit workflow companion. RedSage helps a pentester or auditor run a governed
engagement: it locks the target scope, guides the operator through methodology
phases, verifies evidence the operator pastes in, extracts discovered assets,
tracks findings with evidence gates, compiles audit-ready Markdown reports, and
supports full project export/import.

> **Authorization required.** Use RedSage only for systems you are explicitly
> authorized to test, under written rules of engagement that match the project
> scope you lock into the tool. RedSage is a documentation and workflow tool —
> it does not grant permission to test anything.

RedSage never executes security tooling, launches scans, opens sockets to
targets, or automates attacks. All testing is performed manually by the human
operator outside the application; the operator pastes tool output into RedSage
as evidence.

## What it does

- **Scope lock** — each project has a whitelist/blacklist scope, a rate limit,
  and a lock state. Evidence verification and command-template resolution are
  blocked until the scope is locked, and scope amendments are permanently
  audited.
- **Guided workflow** — a PTES-based 7-phase methodology is seeded per project
  (pre-engagement through reporting), with safe, authorization-aware task
  templates.
- **Evidence handling** — pasted tool output is clipped, regex-redacted
  (bearer tokens, passwords, JWTs, private keys, connection strings), and
  stored as disk artifacts with SHA-256 digests. The database keeps only
  redacted excerpts and metadata.
- **Optional AI verification** — with a `CO_API_KEY`, Cohere reviews evidence
  against the task objective and returns a structured verdict. Without a key,
  verification runs fully offline with a deterministic local verifier and
  nothing leaves the machine.
- **Findings & reports** — findings must link to verified evidence; the report
  builder emits Markdown with a traceable evidence register and readiness
  checks.
- **Export/import** — projects archive to a signed-checksum ZIP that imports
  into a fresh project with all IDs remapped; never overwrites existing data.

## Quickstart

Requirements: Python 3.11+ and Node.js 18+.

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd frontend
npm install
cd ..
```

Optional: copy `.env.example` to `.env` and set `CO_API_KEY` to enable Cohere
verification. Without a key everything runs offline.

### Dev mode (two terminals)

```powershell
# Terminal 1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend
npm run dev
```

Open http://127.0.0.1:5173 (API docs: http://127.0.0.1:8000/docs).

### Prod-like local mode (one process)

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. If `frontend/dist` is missing, the root route
shows the exact build command.

### Convenience scripts

| Task | PowerShell | Shell |
|---|---|---|
| Dev mode (backend + Vite) | `scripts\dev.ps1` | `scripts/dev.sh` |
| Frontend production build | `scripts\build.ps1` | `scripts/build.sh` |
| Prod-like single process | `scripts\run.ps1` | `scripts/run.sh` |
| Full verification (tests + build) | `scripts\verify_all.ps1` | `scripts/verify_all.sh` |

## Landing Page

This repository ships with a static landing page in [`site/`](site/) ready
for GitHub Pages — HTML + CSS only, no build tools, no screenshots required.
All diagrams (workflow, safety, architecture) are inline SVG, so the page is
self-contained and readable in about a minute.

**Product summary:** RedSage v2 is a local-first, human-in-the-loop pentest
workflow companion: scope-safe, evidence-first, report-ready. It locks scope,
guides a 7-phase PTES methodology, verifies pasted evidence, tracks findings
through a draft → confirmed lifecycle, and compiles audit-ready Markdown
reports with a SHA-256 evidence register.

> **Authorized testing only.** RedSage is for systems you are explicitly
> permitted to test under written rules of engagement. It never executes
> tools, scans, or exploits — the human operator performs all testing.

### Preview locally

Option 1 — open `site/index.html` directly in a browser.

Option 2 — from the `site/` folder:

```powershell
python -m http.server 5179
```

Then open http://127.0.0.1:5179.

### Publish with GitHub Pages

1. Commit the `site/` folder to the `main` branch.
2. Open **Settings → Pages** in the repository.
3. Set **Source** to *Deploy from a branch*, **Branch** to `main`, and the
   folder to **`/site`**.
4. Click **Save** — the page goes live at
   `https://<username>.github.io/<repo>/`.

See [`site/README.md`](site/README.md) for edit points (GitHub link and
email placeholders to replace before publishing).

## How evidence, findings, and reports work

1. **Lock scope** — create a project and lock its scope (`in_scope_whitelist`,
   `out_of_scope_blacklist`, `max_rate_limit`). Only locked projects accept
   evidence verification.
2. **Run a task phase** — pick a seeded task (e.g. *2.2 Web Content &
   Directory Discovery*). Suggested commands render only for in-scope targets
   and are copyable, never executed.
3. **Paste evidence** — paste tool output into the Evidence tray. RedSage
   clips and redacts it, stores the artifact on disk, and returns a verdict
   (offline deterministic verifier, or Cohere when a key is configured).
4. **Log findings** — create findings with severity, description, and a linked
   evidence ID; confirmation requires a valid evidence link.
5. **Report** — Report Studio shows readiness warnings and generates a Markdown
   report with scope, methodology, assets, confirmed findings (each with its
   Evidence Ref), and an evidence register appendix.
6. **Export/import** — export the project as a checksummed ZIP; import restores
   it as a brand-new project with remapped IDs.

See `docs/DEMO.md` for a 3-minute safe walkthrough using simulated evidence.

## Repository layout

```
├── backend/          # FastAPI workflow engine: routers, services, models, schemas
├── frontend/         # React + Vite UI (source; build to frontend/dist)
├── tests/            # pytest suite (unit/integration; e2e marked separately)
├── scripts/          # dev/build/run/verify helpers (PowerShell + shell)
├── site/             # static landing page for GitHub Pages (HTML + CSS, inline SVG diagrams)
├── data/
│   └── methodologies/  # baseline PTES methodology JSON (seeded into new projects)
├── docs/             # RUN, SECURITY, DEMO, ARCHIVE_FORMAT
├── requirements.txt  # Python dependencies
└── pytest.ini        # pytest marker configuration
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/redsage.db` | Workflow SQLite database (created on first run) |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | Local server binding |
| `APP_ENV` / `DEBUG` | `development` / `true` | Local server settings |
| `CO_API_KEY` / `COHERE_API_KEY` | unset | Enables Cohere verification; unset = fully offline |

Bind to `127.0.0.1` in local mode and never expose the service to untrusted
networks: the app has **no authentication** by design.

## Tests and build checks

```powershell
python -m pytest -m "not e2e"     # unit + integration tests
python -m compileall backend
cd frontend; npm run build; cd ..
```

The e2e browser suite (`pytest -m e2e`) requires a running server
(`scripts\run.ps1`) and Playwright Chromium.

## Documentation

- `docs/RUN.md` — exact dev and prod-like run commands
- `docs/SECURITY.md` — scope enforcement, redaction, untrusted evidence, offline mode, export/import integrity
- `docs/DEMO.md` — safe 3-minute demo walkthrough
- `docs/ARCHIVE_FORMAT.md` — project archive layout, limits, checksums, remapping
- `EXPLANATION.md` — ground-truth design notes for this public release

## License

MIT — see `LICENSE`.
