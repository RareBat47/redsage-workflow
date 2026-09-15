# RedSage v3 KB Implementation Status

## Verified complete

- Cohere workflow index: `redsage_v3_workflow_cohere_v1`
- Indexed vectors: 3,219
- Model: `embed-english-v3.0`
- Dimensions: 1,024
- Source preview: 366 sources / 3,219 chunks
- Hybrid score ranking: vector + lexical + trust − lab penalty
- Server-side policy filtering for approval, lab scope, tenant scope, and unsafe flags
- Retrieval receipts with query hashes and selected chunk IDs
- Citation response assembly with source path, chunk locator, score, components, and content hash
- Real retrieval smoke test: 8 citations returned for an authorized web-assessment query
- KB tests: 16 passed

## Deliberately deferred

The following are not required for the current goal and will not block this KB milestone:

- Customer-facing roadmap product/UI.
- Multi-tenant persistence and subscription entitlements.
- Hosted billing and customer operations.

## Remaining quality and integration work for the current internal KB

- Rich source metadata (author, license, section/page) for every chunk rather than path/ordinal alone.
- Bounded HTTP/MCP integration for Hermes use.
- Human review of PTES rights and selected source content before external redistribution.
- User-provided methodology book, if legally approved.
- Evaluation cases for internal problem-statement retrieval.

## Current scope conclusion

The current target is an internal, operator-facing workflow knowledge base for RedSage development—not a customer-facing roadmap product. The Cohere vector index, retrieval service, policies, citations, receipts, and tests satisfy the current core-KB milestone; the remaining items are quality/integration work, not subscription-product blockers.
