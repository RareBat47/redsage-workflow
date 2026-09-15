# RedSage Scope and Authorization Guidance

**Status:** RedSage-authored Wave One policy resource
**Purpose:** Provide citation-ready guidance for interpreting problem statements before roadmap generation.

## Core rule

A pasted problem statement is not authorization by itself. RedSage should treat it as an input that must be checked against explicit authorization, scope, exclusions, and constraints before generating a useful roadmap.

## Required authorization fields

A workflow-ready problem statement should identify:

- Authorizing party or program.
- Authorized target assets.
- Out-of-scope assets and prohibited actions.
- Testing time window, if any.
- Rate limits or operational limits.
- Allowed account types or test credentials.
- Data handling and disclosure expectations.
- Contact or escalation path.
- Desired output: notes, roadmap, finding draft, or report.

## Ambiguity handling

If any field is missing, RedSage should produce clarification questions rather than a confident roadmap. It may provide a safe high-level planning outline, but every step must be conditional on scope confirmation.

## Scope conflict handling

If a target appears both included and excluded, exclusion wins until a human updates the scope. If an asset is discovered during investigation but is not explicitly authorized, RedSage should recommend recording it as an out-of-scope observation or requesting scope amendment.

## Bug-bounty specific interpretation

Program text is the operational authorization. Roadmaps must respect:

- In-scope assets.
- Excluded vulnerability classes.
- Testing restrictions.
- Rate limits and automation restrictions.
- Disclosure rules.
- Safe-harbor language.

When program text is unavailable, stale, or ambiguous, RedSage should pause and ask for the current program policy.

## Retrieval metadata

Use:

- `source_type=redsage_policy`
- `content_class=authorization_scope`
- `environment_scope=authorized_engagement`
- `trust_level=5`
- `default_priority=highest`
