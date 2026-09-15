# Source approval and download checklist

Use this reference before downloading any candidate book, repository, standard, dataset, or write-up.

## Candidate record

```text
source_id:
name:
url_or_local_path:
source_type:
intended_purpose:
namespace:
revision_or_edition:
license:
commercial_use_status:
attribution_requirements:
sharealike_or_copyleft:
owner_or_contact:
safety_review:
privacy_review:
selected_paths:
content_hash:
download_status:
operator_approval:
```

## Selection rules

- Approve the exact source, not merely its category.
- Prefer official primary sources for methodology, standards, and technology behavior.
- For GitHub repositories, inspect the README, license, current revision, maintenance signal, and selected file paths before downloading broad content.
- Download documentation, checklists, templates, and safe structured guidance before code or scripts.
- Treat books found on GitHub as unapproved until rights are established; repository availability is not a redistribution license.
- Keep lab/CTF sources in a separate namespace with `environment_scope=lab_only` and down-rank or exclude them for real engagements.
- Keep private examples, customer evidence, secrets, governance/legal material, and restricted standards out of the shared corpus.

## Download verification

A completed source download has all of these:

- The expected files or archive are present.
- The revision/edition is recorded.
- The license file or permission evidence is present.
- The selected content is identified.
- A content hash is recorded.
- No executable code was run during intake.
- The source is marked usable only after completeness and safety review.

If a download times out, mark it `incomplete`, do not index it, and retry with a smaller sparse scope or direct file/archive retrieval.

## First-wave source policy

For workflow generation, begin with one methodology book, RedSage verified domain/safety documents, official OWASP web-app guidance, a targeted CWE/CVSS subset, small authorization/scope references, a stop/escalation taxonomy, and a narrow set of official web-platform documents. Defer tool documentation, broad technology domains, private corpora, OSSTMM, ISO/IEC, and full vulnerability feeds until retrieval quality is proven.
