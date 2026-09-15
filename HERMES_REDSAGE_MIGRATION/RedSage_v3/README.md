# RedSage v2

Clean, decoupled rebuild of RedSage built around the preserved Knowledge Base
(ChromaDB vectors + SQLite metadata). The data in `data/` is a verified copy of
the original project's KB; the pristine recovery copy lives in
`D:\HIGH LEVELS OF WORKS\RedSage_KB_BACKUP` (see its `BACKUP_MANIFEST.md`).

## Architecture

```
RedSage_v2/
├── data/                  # verified KB data (working copy)
│   ├── chroma/            # ChromaDB 1.5.9 persistent store, 9 collections (L2)
│   └── redsage.db         # SQLite: metadata, documents, engagement logs (11 tables)
├── core/                  # zero UI/LLM dependencies, importable standalone
│   ├── config.py          # paths, embedding model, top_k/threshold defaults
│   ├── embeddings.py      # local DeterministicEmbedder (exact v1 algorithm) + optional Cohere
│   └── kb_engine.py       # search, source listing, collection stats, grounded answers
└── interfaces/
    ├── api.py             # FastAPI: /api/health, /api/ask, /api/kb/sources, /api/kb/stats
    └── mcp_server.py      # FastMCP stdio server: kb_search, kb_sources, kb_stats
```

## Knowledge base facts

- Active collection: `redsage_kb_local_v4` (13,385 vectors), distance metric L2.
- Embeddings: local `DeterministicEmbedder` — SHA-256 of the text, first 8 bytes
  scaled to [0, 1] (8 dimensions). Fully offline; no API key needed. Querying
  existing vectors requires this exact embedder (default provider).
- Historical collections (`redsage_kb_local` v1–v3, `redsage_kb_cohere*`) are
  preserved and readable; Cohere collections used `embed-english-v3.0` (1024 dims).
- `redsage.db`: 3,740 kbdocuments (17,600 chunks), 17 kbsources
  (playbooks, books, HackTricks, PayloadsAllTheThings, GTFOBins, WADComs,
  The Hacker Recipes), plus engagement/finding/chat history.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Python 3.11+ recommended (verified against 3.14 / chromadb 1.5.9).

## Running

HTTP API (http://127.0.0.1:8000/docs for interactive docs):

```
.venv\Scripts\python -m uvicorn interfaces.api:app --port 8000
```

MCP stdio server (for OpenCode / AI agents):

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
| `REDSAGE_CHROMA_DIR` | `data/chroma` | ChromaDB directory |
| `REDSAGE_DB` | `data/redsage.db` | SQLite database |
| `REDSAGE_COLLECTION` | `redsage_kb_local_v4` | Active collection |
| `REDSAGE_EMBEDDING_PROVIDER` | `local` | `local` or `cohere` |
| `REDSAGE_TOP_K` | `5` | Default result count |
| `REDSAGE_SCORE_THRESHOLD` | `0.15` | Minimum citation score |
| `COHERE_EMBED_MODEL` | `embed-english-v3.0` | Cohere model (optional) |
| `CO_API_KEY` / `COHERE_API_KEY` | unset | Enables Cohere embedder |

## Important notes

- Opening a ChromaDB client on `data/chroma` rewrites `chroma.sqlite3`
  (harmless internal bookkeeping; vector data is untouched). The pristine,
  hash-verified recovery copy stays in `RedSage_KB_BACKUP\data`.
- The local embedder is hash-based (8 dims), so vector distances are not
  semantic. Retrieval quality comes from the lexical rerank + metadata boosts
  in `core/kb_engine.py`, ported unchanged from v1.
- To re-ingest with semantic embeddings later, set the Cohere provider
  (`pip install cohere` + API key) and build a new collection; never mix
  providers inside one collection.
