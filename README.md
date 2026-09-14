# RedSage v2 v3 under development with proper care 🙌

Local-first, single-operator, **human-in-the-loop** penetration testing and
audit workflow companion. The operator manually runs any tooling outside the
application and pastes the output in as evidence. RedSage validates scope,
guides workflow phases, verifies submitted evidence (optionally with Cohere),
extracts discovered assets, tracks findings with evidence gates, compiles
audit-ready Markdown reports, and supports full project export/import.

RedSage never executes security tooling, launches scans, opens sockets to
targets, or automates attacks.

## Repository layout

```
RedSage_v2/
├── core/            # preserved KB engine (ChromaDB + SQLite) - do not modify
├── data/            # SQLite DB, project artifacts, preserved chroma store
├── backend/         # FastAPI workflow engine + services + routers
├── frontend/        # React + Vite UI (frontend/src -> frontend/dist)
├── interfaces/      # legacy KB FastAPI + MCP interfaces
├── tests/           # pytest suite
├── scripts/         # dev/build/run helpers (PowerShell + shell)
├── docs/            # RUN, DEMO, SECURITY, ARCHIVE_FORMAT
└── core/            # untouched knowledge base engine
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd frontend
npm install
cd ..
```

Python 3.11+ recommended (verified against 3.14 / chromadb 1.5.9). Node 18+.

Optional: copy `.env.example` to `.env` and set `CO_API_KEY` to enable Cohere
verification. Without a key the application runs fully offline with a
deterministic local verifier.

## Run: dev mode (two terminals)

Backend:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`. The backend enables CORS for the Vite origin.
API docs: `http://127.0.0.1:8000/docs`.

## Run: prod-like local mode (single process)

Build the UI, then run only the backend; FastAPI serves `frontend/dist` and the
API from the same origin.

```powershell
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. If `frontend/dist` is missing, the root route
shows a message with the exact build command.

## Convenience scripts

| Task | PowerShell | Shell |
|---|---|---|
| Dev mode (backend + Vite) | `scripts\dev.ps1` | `scripts/dev.sh` |
| Frontend production build | `scripts\build.ps1` | `scripts/build.sh` |
| Prod-like single process | `scripts\run.ps1` | `scripts/run.sh` |

## Tests and build checks

```powershell
python -m pytest
python -m compileall backend
cd frontend
npm run build
```

## Documentation

- `docs/RUN.md` - dev and prod-like run instructions
- `docs/DEMO.md` - safe demo walkthrough
- `docs/SECURITY.md` - scope enforcement, redaction, untrusted evidence, offline mode, export/import integrity
- `docs/ARCHIVE_FORMAT.md` - project archive layout, limits, checksums, remapping rules

## Knowledge base engine (core/)

The preserved KB engine is importable standalone and untouched by the workflow
application.

- Active collection: `redsage_kb_local_v4` (13,385 vectors), distance metric L2.
- Embeddings: local `DeterministicEmbedder` (SHA-256 based, 8 dims). Fully
  offline; querying existing vectors requires this exact embedder.
- Historical collections (`redsage_kb_local` v1-v3, `redsage_kb_cohere*`) are
  preserved and readable.
- `data/redsage.db` holds KB metadata and documents plus workflow tables.

HTTP API for the KB (independent of the workbench backend):

```
.venv\Scripts\python -m uvicorn interfaces.api:app --port 8000
```

MCP stdio server:

```
.venv\Scripts\python -m interfaces.mcp_server
```

Direct library use:

```python
from core.kb_engine import KBEngine

engine = KBEngine()
for citation in engine.search("SQL injection bypass WAF"):
    print(citation.score, citation.source, citation.title)
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/redsage.db` | Workflow SQLite database |
| `APP_ENV` / `DEBUG` / `PORT` / `HOST` | development / true / 8000 / 127.0.0.1 | Local server settings |
| `CO_API_KEY` / `COHERE_API_KEY` | unset | Enables Cohere verification/suggestions |
| `REDSAGE_CHROMA_DIR` | `data/chroma` | ChromaDB directory (core) |
| `REDSAGE_DB` | `data/redsage.db` | KB SQLite database (core) |
| `REDSAGE_COLLECTION` | `redsage_kb_local_v4` | Active KB collection (core) |
| `REDSAGE_EMBEDDING_PROVIDER` | `local` | `local` or `cohere` (core) |
| `REDSAGE_TOP_K` | `5` | Default KB result count (core) |
| `REDSAGE_SCORE_THRESHOLD` | `0.15` | Minimum citation score (core) |
| `COHERE_EMBED_MODEL` | `embed-english-v3.0` | Cohere embed model (optional) |

## Important notes

- `core/` and `data/chroma/` are preserved. Opening a ChromaDB client rewrites
  `chroma.sqlite3` (harmless internal bookkeeping); vector data is untouched.
- Evidence is stored as disk artifacts under `data/projects/{project_id}`;
  the database holds only metadata and redacted excerpts.
- Treat pasted logs as untrusted data; RedSage clips, redacts, and XML-bounds
  them before any AI call and requires JSON-only output.
- Binding defaults to `127.0.0.1`. Do not expose the service to untrusted
  networks.
