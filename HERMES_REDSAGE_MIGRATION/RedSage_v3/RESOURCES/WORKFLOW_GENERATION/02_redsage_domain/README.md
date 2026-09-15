# RedSage v3 KB

This directory is the new governed knowledge-base boundary for RedSage v3.

It is intentionally separate from the preserved `core/` compatibility engine.
The current implementation contains provider-neutral contracts only; the next
vertical slice will add a Cohere embedding adapter and a read-only migration
adapter over the v2 corpus.

## Cohere policy

Cohere is an approved provider for semantic indexing in this KB, but no API key
is copied from v2 or written into this repository. The v2 key is loaded only
from the operator's existing local environment when the user explicitly enables
an ingestion/indexing run. Keys must remain in `.env`, a secret manager, or the
Hermes vault—not in source, tests, logs, archives, or documents.

Cohere index profiles must record the model, input type, dimensions, and metric.
They must never be mixed with the deterministic v2 collection. Local mode
remains available through the compatibility adapter.

## Planned structure

```text
KB/
├── contracts.py       # stable records returned by every backend
├── repository.py      # read/write metadata abstraction (next)
├── policies.py        # tenant, project, content-use and egress rules (next)
├── retrieval.py       # hybrid retrieval and citation assembly (next)
├── embeddings/
│   └── cohere.py      # Cohere document/query embeddings (next)
├── adapters/
│   └── v2_compat.py  # read-only adapter for preserved v2 corpus (next)
├── ingestion/         # versioned, approved, atomic ingestion (next)
├── migrations/        # metadata import and verification (next)
└── tests/
```

The initial corpus is one user-provided workflow/problem-solving book. The KB is designed for controlled updates: every new source or revision receives a new immutable version, is reprocessed and re-embedded with Cohere, evaluated, human-approved, and published without deleting the prior active version.

The KB must not authorize scope changes, finding confirmation, proposal approval,
security-tool execution, customer communication, or deletion on its own.
