# Workflow-generation retrieval evaluation

Use this reference after extraction and embedding, before publishing a KB version.

## Query groups

Evaluate at least one query from each group:

1. Incomplete authorization or ambiguous scope.
2. Initial authorized web-application assessment planning.
3. Authentication, session, authorization, or access-control problem statement.
4. Evidence sufficiency, severity, remediation, or reporting.
5. Irrelevant or out-of-scope request.
6. Explicit lab/CTF problem statement.

## Required checks

- Returned citations identify source, revision, document/chunk, and page/path locator.
- Scope and stop-condition guidance outranks convenience or technique content.
- Lab/CTF material is excluded or down-ranked for real-engagement queries.
- Private/project/customer content cannot cross its policy boundary.
- Taxonomy matches do not become confirmed findings.
- Retrieved content is marked untrusted before model use.
- The result distinguishes no result, policy-blocked result, stale source, and low-trust fallback.
- Query classification is exposed and scope/authorization classification takes precedence over technical categories.
- Scope/stop-policy sources outrank technical guidance for ambiguous authorization queries.
- Offline retrieval remains available when remote providers are disabled.

## Publication gate

Publish only after:

- The source manifest is complete.
- Extraction samples are human-reviewed.
- Cohere profile and batch receipts are recorded.
- Citation locators are accurate.
- Namespace and policy negative tests pass.
- Unsafe or irrelevant material is excluded.
- The previous active index remains available for rollback.
