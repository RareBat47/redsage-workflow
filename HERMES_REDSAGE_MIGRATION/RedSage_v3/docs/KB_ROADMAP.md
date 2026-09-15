# RedSage v3 Knowledge Base Roadmap

**Status:** Saved planning baseline
**Scope:** Internal, operator-facing RedSage security workflow assistant
**Customer-facing roadmap UI:** Deferred

## Purpose

RedSage v3 will use several separate, governed knowledge bases instead of one blended corpus. Each KB has a distinct purpose, source policy, retrieval behavior, and safety boundary. Separation prevents lab material, planning guidance, assessment guidance, customer evidence, and product policy from being confused with one another.

## KB inventory

### KB-01 — Workflow and Roadmap Ideation KB

**Identifier:** `redsage_v3_workflow_cohere_v1`

**Status:** Core version built and verified.

**Purpose:** Interpret a pasted authorized pentesting question, bug-bounty problem statement, or assessment brief and generate internal roadmap context.

**Produces:**

- Problem classification.
- Missing clarification questions.
- Authorization and scope gates.
- Relevant methodology phases.
- Initial hypotheses.
- Candidate tasks and Steps.
- Expected evidence.
- Stop conditions.
- Human approval points.
- Source citations and retrieval receipt.

**Current verified baseline:**

- 366 staged sources.
- 3,219 Cohere vectors.
- Cohere `embed-english-v3.0`.
- 1,024 dimensions.
- Hybrid ranking, policy filtering, citations, and receipts.

**Primary consumers:** Internal roadmap assembler, Hermes workflow assistant.

---

### KB-02 — Web Application Assessment Guidance KB

**Identifier:** `redsage_v3_assessment_web_cohere_v1`

**Status:** Planned next phase.

**Purpose:** Guide the operator through the next phase after roadmap ideation: manual, authorized Web Application assessment and interpretation of observations.

**Produces:**

- Preconditions.
- Assessment objectives.
- What to observe.
- Manual verification guidance.
- Evidence requirements.
- False-positive checks.
- Stop/escalation conditions.
- OWASP/CWE mappings.
- Remediation context.
- Citations and uncertainty.

**Initial source families:**

- OWASP WSTG test objectives.
- OWASP ASVS requirements.
- Selected OWASP Cheat Sheets.
- CWE web/application weaknesses.
- CVSS guidance.
- MDN and relevant HTTP/browser standards.
- RedSage scope, evidence, safety, and reporting policies.
- Carefully selected responsible write-ups.

**Boundary:** Guidance and interpretation only; no tool execution or autonomous testing.

---

### KB-03 — API Assessment Guidance KB

**Identifier:** `redsage_v3_assessment_api_cohere_v1`

**Status:** Deferred until Web Application assessment guidance is validated.

**Purpose:** Support manual authorized API assessment after the web-app workflow is stable.

**Produces:**

- API-specific reconnaissance and context questions.
- Authentication and authorization checks.
- Object-level and function-level authorization guidance.
- Schema and input-validation review objectives.
- Rate-limit and error-behavior observations.
- Evidence requirements.
- False-positive checks.
- API-specific reporting and remediation context.

**Initial source families:**

- OWASP API Security Top 10.
- OWASP REST, GraphQL, and WebSocket guidance.
- ASVS API-relevant requirements.
- Official HTTP/API/framework documentation.
- CWE/CVSS references.
- RedSage policies.

**Boundary:** API guidance only; execution remains manual and externally authorized.

---

### KB-04 — Authentication, Identity, and Session KB

**Identifier:** `redsage_v3_assessment_identity_cohere_v1`

**Status:** Planned component or independently addressable sub-KB.

**Purpose:** Provide deeper guidance for authentication, identity, session, account recovery, MFA, OAuth, SAML, JWT, and cookie-related assessment work.

**Produces:**

- Identity-flow mapping.
- Authentication hypotheses.
- Session-management observations.
- Account-recovery review objectives.
- MFA and token-handling checks.
- Evidence and stop conditions.
- Remediation and verification guidance.

**Source families:**

- OWASP WSTG identity/session sections.
- OWASP Authentication, Session Management, OAuth2, JWT, MFA, and Password Cheat Sheets.
- ASVS V2/V3 and relevant requirements.
- MDN/RFC identity and cookie references.
- CWE mappings.

**Boundary:** May be implemented as a filterable layer of the Web Application KB before becoming a separate physical index.

---

### KB-05 — Authorization and Business-Logic Assessment KB

**Identifier:** `redsage_v3_assessment_authorization_cohere_v1`

**Status:** Planned component or independently addressable sub-KB.

**Purpose:** Support assessment of access control, object ownership, workflow state, privilege boundaries, and business-logic assumptions.

**Produces:**

- Object/function authorization hypotheses.
- Workflow and state-transition analysis.
- Controlled comparison objectives.
- Minimal-evidence guidance.
- False-positive and impact checks.
- CWE/OWASP mapping.
- Remediation guidance.

**Source families:**

- OWASP authorization and access-control guidance.
- WSTG authorization sections.
- ASVS access-control requirements.
- Business-logic security guidance.
- Responsible reports focused on reasoning and impact.

**Boundary:** No broad enumeration, destructive action, or unauthorized access instructions.

---

### KB-06 — Evidence, Findings, and Reporting KB

**Identifier:** `redsage_v3_evidence_reporting_cohere_v1`

**Status:** Planned.

**Purpose:** Help interpret operator-collected evidence, distinguish observations from confirmed findings, and produce traceable internal reporting material.

**Produces:**

- Evidence sufficiency checks.
- Observation/hypothesis/finding separation.
- Finding structure.
- Impact and severity reasoning.
- Reproduction-summary guidance.
- Remediation verification.
- Evidence-register requirements.
- Report citations and limitations.

**Source families:**

- RedSage evidence and reporting rules.
- OWASP reporting guidance.
- CWE and CVSS.
- Responsible disclosure/report examples with rights and redaction review.
- Authorized assessment report templates.

**Boundary:** Cannot confirm a finding without project-scoped evidence and explicit human review.

---

### KB-07 — Scope, Authorization, and Stop-Condition Policy KB

**Identifier:** `redsage_v3_policy_cohere_v1`

**Status:** Core policy layer already authored; should remain highest-priority and separately governed.

**Purpose:** Prevent unsafe or unauthorized roadmap and assessment behavior.

**Produces:**

- Authorization clarification gates.
- Scope interpretation.
- Exclusion handling.
- Rate/time-limit checks.
- Pause and escalation rules.
- Human approval requirements.
- Lab-versus-real-engagement separation.

**Current resources:**

- `RESOURCES/WORKFLOW_GENERATION/09_scope_authorization/REDSAGE_SCOPE_AUTHORIZATION_GUIDANCE.md`
- `RESOURCES/WORKFLOW_GENERATION/10_stop_escalation/REDSAGE_STOP_ESCALATION_TAXONOMY.md`

**Boundary:** Policy results are hard gates, not ordinary ranking suggestions.

---

### KB-08 — Lab and CTF Reasoning KB

**Identifier:** `redsage_v3_lab_cohere_v1`

**Status:** Planned, separate from real-engagement KBs.

**Purpose:** Provide reasoning examples from deliberately vulnerable labs and CTFs.

**Produces:**

- Clue-to-hypothesis reasoning.
- Controlled validation sequences.
- Educational evidence interpretation.
- Learning-oriented Mentor context.

**Required metadata:**

- `source_type=lab`.
- `environment_scope=lab_only`.
- `retrieval_default=downranked_or_excluded`.
- License/permission status.

**Boundary:** Lab assumptions must never be presented as authorization or normal production behavior.

---

### KB-09 — Technology and Platform Context KB

**Identifier:** `redsage_v3_technology_web_cohere_v1`

**Status:** Small Web Application subset planned; broader versions deferred.

**Purpose:** Explain normal platform behavior and support technology-aware roadmap branches.

**Initial scope:**

- HTTP.
- Cookies and sessions.
- Browser security.
- Same-origin policy.
- CORS and CSP.
- TLS basics.
- Common web servers/frameworks selected for actual evaluation cases.

**Later scopes:**

- API platforms.
- Cloud.
- Mobile.
- Network.
- Containers and orchestration.

**Source policy:** Prefer official documentation and standards; preserve version and publication metadata.

---

### KB-10 — Product and Domain Compatibility KB

**Identifier:** `redsage_v3_product_domain_v1`

**Status:** Partially staged from verified v2 and v3 documentation.

**Purpose:** Keep KB-driven roadmap and assessment guidance compatible with RedSage's own domain model and safety posture.

**Contains:**

- Verified v2 implementation behavior.
- v2 methodology and state model.
- Scope and evidence rules.
- Findings and report behavior.
- Archive and audit behavior.
- v3 KB contracts and policies.
- Relevant tests and acceptance rules.

**Boundary:** Code and executed tests outrank stale documentation; no secrets, databases, customer data, or development clutter.

---

### KB-11 — Organization-Private Knowledge KB

**Identifier:** `redsage_v3_private_org_<organization>_v1`

**Status:** Deferred.

**Purpose:** Store an organization's private playbooks, standards, architecture conventions, and approved internal procedures.

**Boundary:** Separate tenant/private index and access policy; never blended into the shared reference corpus by default.

---

### KB-12 — Project Evidence and Engagement Context Index

**Identifier:** `redsage_v3_project_<project>_evidence_v1`

**Status:** Deferred until the v3 project/evidence domain is implemented.

**Purpose:** Search project-local evidence and context for the operator during an engagement.

**Contains:**

- Redacted evidence excerpts.
- Artifact metadata.
- Project assets.
- Project decisions.
- Approved scope and methodology context.

**Boundary:** Never automatically promoted to shared knowledge; retention, deletion, export, and access are project/customer policy decisions.

---

### KB-13 — Retrieval and Audit Receipt Store

**Identifier:** `redsage_v3_retrieval_receipts_v1`

**Status:** Basic file receipts implemented; durable domain store planned.

**Purpose:** Explain and reproduce what the KB returned to an operator or Hermes.

**Records:**

- Query hash.
- Actor type.
- Project/context scope.
- Query classification.
- Policy version.
- Ranking profile.
- Index profile.
- Selected source/version/document/chunk IDs.
- Score components.
- Filtered counts/reasons.
- Timestamp.

**Boundary:** Store minimal sensitive data; raw queries and raw evidence are not retained by default.

---

## Recommended build order

1. **KB-01:** Keep roadmap ideation stable.
2. **KB-07:** Make policy gates authoritative and highest priority.
3. **KB-10:** Preserve RedSage domain compatibility.
4. **KB-02:** Build Web Application assessment guidance.
5. **KB-06:** Add evidence, findings, and reporting support.
6. **KB-04:** Deepen identity/session guidance as a filter or sub-index.
7. **KB-05:** Deepen authorization/business-logic guidance as a filter or sub-index.
8. **KB-09:** Add only the web technology context required by evaluation cases.
9. **KB-08:** Add lab/CTF material in an isolated collection.
10. **KB-03:** Build the API assessment KB.
11. **KB-13:** Move receipts from files into the durable v3 audit domain.
12. **KB-11/KB-12:** Add private organization and project evidence indexes only after tenancy and custody boundaries exist.

## Global rules for every KB

- Every source gets an immutable version and content hash.
- Every chunk carries provenance and policy metadata.
- Every remote embedding/LLM call is explicit and redacted.
- Every result is treated as untrusted reference material.
- No KB can authorize testing or mutate RedSage security state by itself.
- Lab-only content is isolated and excluded by default from real engagements.
- Customer evidence stays separate from shared reference knowledge.
- Published index versions remain available for rollback.
- No source is considered commercially usable merely because it is hosted on GitHub.
- Cohere embedding profiles are isolated by model, dimensions, and input type.
- Every KB change updates the RedSage v2-to-v3 feature map and records verification evidence.
