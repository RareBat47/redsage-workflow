REDSAGE v3 RESOURCE INTAKE PLAN — WAVE ONE
============================================

Decision status
---------------
Approved for planning by the operator after Claude review. This folder is an
intake plan and manifest location. No source material has been downloaded,
embedded, or published yet.

Primary objective
-----------------
Build a workflow-roadmap KB that can interpret a pasted authorized pentesting
question, bug-bounty problem statement, or web-application assessment brief and
produce a cited initial roadmap containing clarification questions, scope gates,
ordered phases, hypotheses, tasks, evidence requirements, stop conditions, and
human approval points.

Resource groups to add
======================

A. ONE METHODOLOGY BOOK — REQUIRED FIRST SOURCE
------------------------------------------------
What to add:
- One legally usable book about bug hunting, penetration testing, security
  assessment methodology, or structured security problem-solving.
- Prefer material with clear commercial-use permission or a license that allows
  the intended hosted subscription use; otherwise obtain permission/license or
  use only a legally permitted paraphrase/reference treatment.

Metadata to capture:
- Title, author, edition, publisher, source URL/file name.
- License or permission evidence and attribution requirements.
- SHA-256 hash, upload date, page count, language.

Purpose:
- Supply the core engagement and problem-solving workflow.
- Teach roadmap sequencing, hypotheses, prerequisites, evidence, and reporting.
- Provide page-level citations for generated roadmap guidance.

B. OWASP WEB APPLICATION CORE
-----------------------------
What to add:
- OWASP Web Security Testing Guide.
- OWASP Top 10 for the selected current edition.
- OWASP Application Security Verification Standard.
- OWASP Cheat Sheet Series items directly relevant to web testing.
- OWASP API Security Top 10 is deferred to Wave Two unless needed by the book.

Metadata to capture:
- Exact project/document version, URL, section identifier, license, attribution,
  retrieval date, and content hash.

Purpose:
- Provide recognized web-application testing coverage.
- Map a problem statement to security control families and test objectives.
- Define what should be verified without treating a category match as proof.
- Give defensible citations for roadmap and report output.

C. CWE AND CVSS TAXONOMY CORE
-----------------------------
What to add:
- CWE weakness definitions relevant to web applications.
- CVSS specification and official scoring guidance.
- NVD/CVE data only where it directly supports the selected web-application
  technology set; avoid ingesting the entire feed in Wave One.

Metadata to capture:
- Identifier, version, publication/update date, source URL, license/terms,
  affected categories, and whether the entry is current or retired.

Purpose:
- Normalize vulnerability language.
- Map observations and hypotheses to weakness classes.
- Support severity reasoning without automatic finding confirmation.
- Improve duplicate detection and finding organization.

D. SCOPED WEB-APPLICATION TECHNOLOGY DOCUMENTATION
----------------------------------------------------
What to add:
- A small, explicitly selected set only: HTTP, cookies, sessions, authentication,
  authorization, browser security, TLS basics, common web architecture, and the
  first target framework/server technologies we choose.
- Official documentation only where possible.
- Start with web applications; APIs, cloud, mobile, and network documentation
  are deferred to Wave Two.

Metadata to capture:
- Product/framework and version, official URL, publication date, license,
  retrieval date, content hash, and supported target type.

Purpose:
- Help identify technologies and normal behavior.
- Improve roadmap branching and prerequisite checks.
- Explain what an observed behavior may mean.
- Ground remediation and validation guidance.

E. VETTED GITHUB METHODOLOGY REPOSITORIES — DOCS ONLY
------------------------------------------------------
What to add:
- A small number of maintained repositories containing methodology checklists,
  assessment planning, evidence organization, reporting templates, or safe
  workflow documentation.
- Documentation and structured templates only in Wave One.
- No automatic ingestion or execution of repository code/scripts.

Required review before acceptance:
- Repository owner and reputation.
- Maintenance activity and version/commit reviewed.
- License and commercial reuse terms.
- Security/content review.
- Duplicate/contradiction review against the primary methodology book.

Purpose:
- Add practical checklist and task structures.
- Improve Step templates and report fields.
- Compare community workflow patterns without treating community material as
  authoritative.

F. RESPONSIBLE BUG-BOUNTY WRITE-UPS — SMALL REDACTED SET
----------------------------------------------------------
What to add:
- A few legally reusable, public or platform-published write-ups.
- Prefer examples that explain root cause, validation, impact, evidence, and
  remediation.
- Select examples aligned with web applications and the chosen technology set.

Required processing:
- Remove credentials, tokens, private data, identifying target details, and
  unnecessary payload material.
- Preserve author, title, date, URL, license/permission, and attribution.
- Label as an example/write-up, not normative methodology.

Purpose:
- Teach the difference between a clue, hypothesis, validated observation, and
  confirmed finding.
- Improve impact reasoning and report quality.
- Show how evidence and remediation are communicated.

G. DELIBERATELY VULNERABLE LAB/CTF WRITE-UPS — SEPARATE COLLECTION
-------------------------------------------------------------------
What to add:
- A small, clearly authorized set of lab or CTF explanations.
- Only material suitable for controlled educational environments.
- Prefer reasoning, decision points, and evidence interpretation over payloads.

Required processing:
- Store with source_type=lab and environment_scope=lab_only.
- Keep in a separate collection/index namespace from real-engagement guidance.
- Down-weight or exclude by default for real engagement queries.
- Make available only when the problem statement is explicitly lab/CTF scoped.

Purpose:
- Teach investigative sequencing and hypothesis formation.
- Provide controlled examples of clues leading to findings.
- Prevent lab permissions and assumptions from contaminating real roadmaps.

H. REDSAGE PRODUCT AND DOMAIN DOCUMENTATION
-------------------------------------------
What to add:
- Verified RedSage v2 behavior from code and tests.
- `START_HERE.md`, `EXPLANATION.md`, `docs/SECURITY.md`, methodology JSON,
  API contracts, and relevant test behavior.
- RedSage v3 KB contracts, safety rules, and approved product decisions.

Required processing:
- Code and executed tests outrank stale prose.
- Preserve source file and test references.
- Keep product rules distinct from external security knowledge.
- Do not ingest secrets, `.env` files, customer data, or development clutter.

Purpose:
- Keep generated roadmaps compatible with RedSage's scope, evidence, approval,
  audit, findings, and reporting model.
- Prevent migration regressions.
- Give Hermes accurate bounded tool and workflow context.

I. AUTHORIZATION AND SCOPE-VERIFICATION REFERENCES — ADDED GAP
---------------------------------------------------------------
What to add:
- Legally reusable bug-bounty platform scope and rules guidance.
- Public authorization and rules-of-engagement checklists.
- Defensive, high-level guidance for interpreting ambiguous scope language.
- Avoid legal advice; mark organization-specific decisions as policy-owned.

Purpose:
- Put authorization and scope before every roadmap phase.
- Trigger clarification or pause when permission is ambiguous.
- Prevent the highest-cost failure: generating a roadmap for an unauthorized
  target or activity.

J. STOP-CONDITION AND ESCALATION TAXONOMY — ADDED GAP
------------------------------------------------------
What to add:
- A small curated set of defensive workflow gate definitions.
- Conditions for pause, clarification, human approval, evidence insufficiency,
  suspected impact, out-of-scope discovery, and unsafe request handling.
- RedSage-authored policy is preferred for these rules.

Purpose:
- Tell the Planner when to stop rather than continue.
- Make escalation behavior retrievable and citeable.
- Keep human approval points explicit in generated roadmaps.

Wave One inclusion recommendation
=================================

The detailed candidate list is in `RESOURCES/WAVE_ONE_CANDIDATE_SOURCES.txt`.

Include:
- A: one operator-provided methodology book.
- B: OWASP WSTG, ASVS, Top 10, and selected Cheat Sheets.
- C: CWE web/application subset and current CVSS guidance.
- D: small authorization/scope-verification reference set.
- E: selected MDN/RFC and first web-technology documentation.
- F: individually reviewed, permissively licensed GitHub documentation.
- G: small redacted and rights-reviewed responsible write-up set.
- H: separate lab/CTF collection, down-weighted by default.
- I: verified RedSage product/domain documentation.
- J: RedSage-authored stop-condition/escalation taxonomy.

Do not download or ingest unnamed GitHub candidates until their repository,
license, commit, maintenance, content, and safety review is complete.

The operator must approve the specific source list before download.
Defer to Wave Two:
- API-focused documentation beyond what the first web-app set requires.
- Security tool documentation.
- Threat-modeling resources.
- Cloud, mobile, network, and specialized technology corpora.
- OSSTMM until commercial redistribution rights are confirmed.
- ISO/IEC material unless separately licensed; do not copy it into the KB based
  only on general availability.
- Private historical examples and governance/legal material in the shared KB.

Do not ingest by default
========================

- Credentials, API keys, tokens, private keys, or personal data.
- Customer evidence into the shared corpus.
- Unlicensed books, paid course content, or proprietary standards.
- Arbitrary web scraping dumps.
- Unreviewed repositories or executable code.
- Malware, destructive payloads, persistence content, or unauthorized automation.
- Lab instructions without explicit lab-only labeling.
- Duplicate or obsolete sources without version and trust metadata.

Per-source approval checklist
=============================

Before ingestion, every source needs:

[ ] Human approval for this category and specific source.
[ ] Commercial-use/redistribution permission confirmed and recorded.
[ ] Attribution requirements captured.
[ ] ShareAlike/copyleft implications recorded.
[ ] Owner or point of contact recorded where applicable.
[ ] Source URL/file and exact version recorded.
[ ] SHA-256 content hash recorded.
[ ] PII/credential scan completed.
[ ] Unsafe-content review completed.
[ ] Source type and environment scope assigned.
[ ] Trust level assigned.
[ ] Retrieval namespace/collection assigned.
[ ] Expected roadmap use documented.
[ ] Citation locator strategy verified.

Expected conversion output
===========================

Each approved source should produce:

1. Immutable source manifest.
2. Extracted normalized text.
3. Chapter/section/page structure.
4. Redacted and classified content.
5. Semantic chunks with source/version/document/chunk IDs.
6. Structured workflow concepts where appropriate.
7. Decision rules, prerequisites, evidence expectations, and stop conditions.
8. Cohere embedding profile and batch receipt.
9. Citation/evaluation records.
10. Human approval and publication record.

Roadmap output target
=====================

For a pasted problem statement, the published KB should support:

1. Problem classification.
2. Missing clarification questions.
3. Authorization and scope checks.
4. Technology and asset interpretation.
5. Security hypotheses.
6. Ordered methodology phases.
7. Tasks and Steps.
8. Expected evidence for each Step.
9. Stop conditions and escalation points.
10. Human approval requirements.
11. Finding/reporting structure.
12. Source citations, confidence, and uncertainty.

The KB provides cited, policy-filtered guidance. It does not execute tools,
expand authorization, confirm findings, approve workflow changes, or delete
customer data automatically.

First ingestion order
======================

1. User-provided methodology book.
2. RedSage product/safety/domain documentation.
3. OWASP web-app core.
4. CWE/CVSS core.
5. Authorization/scope references.
6. Stop-condition/escalation taxonomy.
7. Small official web-technology set.
8. Vetted GitHub documentation.
9. Responsible write-ups.
10. Separate lab/CTF collection.

No Cohere indexing begins until the first source passes the checklist and its
extraction has been inspected by the operator.
