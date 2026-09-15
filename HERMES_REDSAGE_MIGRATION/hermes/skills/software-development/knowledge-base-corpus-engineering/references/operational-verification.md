# Operational Verification

Use independent checks after every KB build or shared retrieval change.

## Index integrity

For each manifest/collection pair:

1. Load the manifest and build receipt.
2. Hash the current manifest.
3. Compare manifest chunk count with the live collection count.
4. Compare manifest chunk IDs with collection IDs.
5. Report stale and missing IDs separately.
6. Treat a changed manifest hash with matching IDs as a changed receipt generation, not as proof that vectors were rebuilt.
7. Refuse reuse when collection model, metadata schema, policy version, source manifest identity, or manifest hash does not match the requested build profile.

A valid result has zero stale IDs, zero missing IDs, and equal manifest/live counts.

## Retrieval verification

Run at least one real query per domain and one consolidated query. Inspect:

- Query classification.
- Returned domain/phase metadata.
- Citation title, locator, source/version/document/chunk IDs, and content hash.
- Candidate count, filtered count, and stable filter reasons.
- Retrieval receipt ID and receipt fields.
- Policy precedence for ambiguous authorization.
- Lab exclusion for authorized engagements.

Do not treat a non-empty result as quality proof; verify that the top results answer the query's intended phase.

## Safety regression

Run cases for:

- Missing authorization.
- Unknown scope.
- Unapproved content.
- Unsafe content.
- Lab-only content in a real engagement.
- Tenant mismatch when tenant context exists.

Ambiguous authorization should return clarification and skip provider/vector retrieval when the roadmap gate can decide locally.

## Hermes/MCP verification

Verify in order:

1. Python import and compilation.
2. Direct stdio server startup.
3. Hermes registration/discovery.
4. `hermes mcp test <server>`.
5. Live bounded tool call in a fresh session.
6. Citation and receipt readback.

Use a small launcher that sets the project working directory when the host launches a stdio server from an arbitrary directory; this makes relative paths deterministic without changing the KB contract.
