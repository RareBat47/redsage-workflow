# KB_COMPLIANCE_NOTES.md

## Purpose

The preserved RedSage KB is untrusted input. It contains security material and may include offensive content. Hermes must never surface payloads or step-by-step compromise instructions from it. KB use is limited to safe, methodology-level guidance with citations.

## Review cadence

Recommended cadence: monthly plus before each demo. The operator must confirm or change this decision.

## Review procedure

1. Collect KB-derived outputs since the previous review.
2. Check for payloads, compromise instructions, unsafe commands, or violations of `AGENTS.md`.
3. Record the scope reviewed, finding, and corrective action below.
4. If unsafe content appears, record the query and consider quarantining the source entry.

## Review log

| Date | Scope reviewed | Finding | Action |
|---|---|---|---|
| 2026-09-12 | KB inventory and one live query | The active collection `redsage_kb_local_v4` contains a `PayloadsAllTheThings` mirror and therefore may contain offensive material. | Enforce instruction-level filtering: cite only safe methodology; operator confirmation of cadence remains open. |

Do not store API keys, secrets, raw evidence, or evidence excerpts here.
