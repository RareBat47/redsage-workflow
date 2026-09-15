# RedSage v3 KB Current Status

## Current milestone

The internal operator-facing multi-KB workflow is validated; customer-facing UI and subscription product work remain deferred.

## Verified populated KBs

| Domain | Collection | Vectors | Status |
|---|---|---:|---|
| Workflow/roadmap ideation | `redsage_v3_workflow_cohere_v1` | 3,219 | Verified |
| Web application assessment | `redsage_v3_assessment_web_cohere_v1` | 2,815 | Verified |
| Evidence/findings/reporting | `redsage_v3_evidence_reporting_cohere_v1` | 2,418 | Verified |
| Identity/session | `redsage_v3_assessment_identity_cohere_v1` | 315 | Verified |
| Authorization/business logic | `redsage_v3_assessment_authorization_cohere_v1` | 183 | Verified |
| API assessment | `redsage_v3_assessment_api_cohere_v1` | 130 | Verified |

All use Cohere `embed-english-v3.0` with 1,024 dimensions and separate policy/schema profiles.

## Verified workflow

```text
Problem statement
→ Authorization/scope gate
→ Consolidated retrieval
→ Policy filtering
→ Roadmap generation
→ Step-specific guidance
→ Operator pastes evidence
→ Evidence sufficiency review
→ Draft finding/report
```

## Latest verification

- KB tests: 80 passed.
- End-to-end engagement cases: 6/6 passed.
- All six populated indexes: manifest/live vector counts match; stale IDs 0; missing IDs 0.
- Hermes consolidated roadmap MCP: connected; one bounded tool discovered.
- Hermes domain MCP tools: workflow, Web Application, evidence/reporting, identity, and API servers registered and tested.
- Lab/CTF KB: empty and intentionally not embedded.

## Next recommended job

Do not add more sources immediately. Run an **operator acceptance test** using one real authorized or explicitly lab-scoped problem statement and inspect:

1. Clarification behavior.
2. Roadmap phase/task/Step usefulness.
3. Correct KB domain selection.
4. Citation accuracy.
5. Retrieval receipt completeness.
6. Evidence-review behavior using sanitized sample evidence.
7. No unauthorized execution or scope expansion.

Record defects as focused fixes, rerun the full tests, then decide whether to build the separate Lab/CTF KB or start RedSage v3 application/domain integration.

## Deferred

- Customer-facing roadmap UI.
- Hosted multi-tenant architecture.
- Subscription plans, quotas, and billing.
- Private organization/project KBs.
- Lab/CTF corpus until approved sources are available.
