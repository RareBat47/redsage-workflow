# RedSage v3 KB Next Phase Proposal

## Decision

Keep the current `workflow-generation` KB as the roadmap-ideation layer. Build a separate, phase-specific KB for **authorized Web Application and API assessment execution support**.

“Execution support” means helping the operator plan and interpret manual work, not RedSage executing scans, opening sockets, generating harmful payloads, or taking action against a target.

## Separation of responsibilities

### Existing KB: roadmap ideation

Input: pasted problem statement or assessment brief.

Output:
- Clarification questions.
- Authorization and scope gates.
- Problem classification.
- Ordered methodology phases.
- Initial hypotheses.
- Proposed tasks and Steps.
- Evidence expectations.
- Stop conditions.

### Next KB: assessment-phase guidance

Input: an approved roadmap Step plus operator-supplied observations or evidence.

Output:
- Preconditions and required context.
- Safe manual verification objectives.
- What to observe.
- Evidence-capture requirements.
- Interpretation of observations.
- False-positive checks.
- Escalation/stop conditions.
- Finding and remediation mapping.
- Citations and uncertainty.

## Recommended next corpus

1. OWASP WSTG test objectives and verification guidance.
2. OWASP ASVS requirements for web applications.
3. OWASP Cheat Sheets for defensive interpretation and remediation.
4. CWE definitions and relationships for observed weaknesses.
5. CVSS guidance for severity reasoning.
6. Selected MDN and RFC material for normal browser/HTTP behavior.
7. RedSage evidence, scope, safety, and reporting policies.
8. A small approved set of responsible write-ups for evidence and false-positive reasoning.
9. API-specific material only after the Web Application phase is stable.

Do not add tool documentation or unrestricted exploit repositories in this phase.

## Proposed collections

```text
redsage_v3_workflow_cohere_v1       # existing roadmap ideation
redsage_v3_assessment_web_cohere_v1 # next Web App assessment guidance
redsage_v3_assessment_api_cohere_v1 # later API guidance
redsage_v3_lab_cohere_v1            # separate lab-only material, later
```

Keep collections separate so roadmap planning, assessment guidance, and lab
material cannot be silently conflated.

## Metadata required for assessment chunks

- `phase`: assessment phase/category.
- `test_objective`.
- `preconditions`.
- `observation_targets`.
- `evidence_type`.
- `false_positive_checks`.
- `stop_conditions`.
- `finding_mapping`.
- `source_type`.
- `environment_scope`.
- `trust_level`.
- `is_approved`.
- `is_unsafe`.
- `source_version_id`.
- `document_id`.
- `locator`.
- `content_hash`.

## Build sequence

1. Freeze the existing roadmap KB and receipt.
2. Select and label assessment-only source sections.
3. Add the assessment metadata schema.
4. Build a new preview manifest; do not modify the roadmap index.
5. Review source selection and estimated Cohere usage.
6. Embed into a new assessment collection.
7. Add phase-aware retrieval and citations.
8. Create evaluation cases for authentication, session management, access control,
   input validation, business logic, HTTP/browser behavior, and API discovery.
9. Verify that the system returns manual guidance and evidence requirements,
   never autonomous execution.
10. Expose a separate bounded MCP tool only after direct tests pass.

## Completion criteria

The next KB phase is complete when:

- The existing roadmap collection remains unchanged.
- The new assessment collection has a matching manifest and verified vector count.
- Every result contains phase, objective, evidence, stop-condition, and citation metadata.
- Scope and authorization policy filtering runs before ranking.
- Lab-only material is excluded from normal authorized assessment retrieval.
- Evaluation cases demonstrate useful phase-specific retrieval.
- No tool execution or harmful autonomous action is introduced.
- Cohere usage, model, dimensions, and build receipt are recorded.
