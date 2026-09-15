# RedSage Workflow Stop and Escalation Taxonomy

**Status:** RedSage-authored Wave One policy resource
**Purpose:** Provide retrieval-ready gates for initial roadmap generation.

## Mandatory pause conditions

The Planner must recommend pause and human clarification when:

- Authorization is missing, expired, contradictory, or not specific to the target.
- The target is absent from the approved scope.
- The target appears in an exclusion or blacklist.
- The problem statement requests destructive, disruptive, deceptive, or persistence activity.
- The requested action would exceed the stated rate, time, or operational limit.
- Evidence contains secrets, credentials, or unrelated personal data.
- A suspected issue cannot be supported by sufficient evidence.
- A lab/CTF assumption is being applied to a real engagement.
- A proposed workflow would require an unapproved external service or data transfer.
- The operator asks RedSage to execute a tool or contact a target.

## Clarification conditions

Ask for clarification before generating a final roadmap when:

- Engagement objective is unclear.
- Scope boundaries are incomplete.
- Target type or technology is unknown and changes the workflow.
- Constraints, timebox, credentials, test accounts, or rate limits are unknown.
- Desired output or evidence standard is not stated.
- The problem statement uses ambiguous severity or impact language.

## Continue conditions

A roadmap may proceed to a human-reviewable draft when:

- Authorization and scope are explicit.
- The target is permitted and exclusions are understood.
- The requested activity is non-destructive and within constraints.
- The roadmap is composed of manual, display-only, or observational steps.
- Evidence expectations and stop conditions are stated.
- Any AI-derived suggestion is marked as a proposal rather than fact.

## Human approval gates

Human approval is required before:

- Applying a generated workflow.
- Adding or changing scope.
- Approving a proposed task.
- Marking evidence as conclusive.
- Confirming a finding.
- Sending a customer-facing report or communication.
- Indexing private/customer material.
- Publishing a new shared KB source or version.

## Retrieval metadata

Use:

- `source_type=redsage_policy`
- `content_class=stop_condition`
- `environment_scope=authorized_engagement`
- `trust_level=5`
- `default_priority=highest`
