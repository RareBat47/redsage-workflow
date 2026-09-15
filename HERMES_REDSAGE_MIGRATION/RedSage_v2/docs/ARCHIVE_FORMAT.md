# RedSage v2: Project Archive Format

Version: `1.0`

A project archive is a single ZIP file created locally by the backend that
contains everything needed to restore one project on another machine. The
archive never contains the global database, `.env`, API keys, or external
configuration.

## ZIP layout

```
manifest.json                 archive metadata + checksums
db/project_data.json          one project's rows as JSON
artifacts/<filename>.txt      full raw evidence artifact files
reports/report.md             generated Markdown report snapshot (optional)
```

`db/project_data.json` contains these row lists, scoped to the exported
project only:

`projects`, `scopes`, `scope_amendments`, `phases`, `tasks`,
`workflow_proposals`, `assets`, `evidence`, `findings`, `audit_events`

## manifest.json

```json
{
  "format_version": "1.0",
  "exported_at_utc": "2026-09-08T11:00:00Z",
  "project_id": "<uuid>",
  "counts": { "projects": 1, "evidence": 3, "...": 0 },
  "checksums": [
    { "path": "db/project_data.json", "sha256": "...", "size_bytes": 1234 }
  ]
}
```

`checksums` lists every non-manifest member. Import verifies every required
member exists in the manifest and that its SHA-256 matches before writing any
rows.

## Limits and safety rules

| Rule | Value |
|---|---|
| Max archive bytes | 100 MB |
| Max archive members | 1,000 |
| Max single member bytes | 10 MB |
| Required members | `db/project_data.json` plus one artifact per evidence row |
| Member paths | must be relative; absolute paths, backslashes, empty/dot segments, and `..` traversal are rejected |
| Artifact extensions | `.txt` and `.log` only |

Import rejects archives with a missing, unreadable, or unsupported-version
`manifest.json`, missing required members or checksums, checksum mismatches,
or unsafe member names, returning HTTP 400 without creating data.

## ID remapping on import

Imported projects never overwrite an existing project:

- A new random project ID is generated.
- Every imported row (scope, amendments, phases, tasks, assets, evidence,
  findings, proposals, audit events) receives a new ID.
- Foreign keys are remapped consistently: `phase_id`, `task_id`,
  `source_task_id`, `evidence_id`, `created_task_id`, and audit `entity_id` /
  `entity_type` references point at the newly created rows.
- Evidence IDs are re-minted as `EVID-XXXXXXXXXX` to stay globally unique.
- Evidence artifact files are written under
  `data/projects/{new_project_id}/artifacts/` and the recorded
  `file_path`, `file_size_bytes`, and `sha256_hash` are recomputed from the
  extracted bytes.
- `project_id` references in `audit_events.details` (`task_id`,
  `evidence_id`, `proposal_id`) are also remapped where present.

A failed import rolls back the database transaction and removes only the newly
created project directory, leaving existing projects and the shared database
untouched.

## Export filename

```
redsage_project_{project_id}_{YYYYMMDD}.zip
```

## Backward compatibility

- Evidence rows that still carry a legacy `raw_content` value are exported as
  artifact files when no disk artifact is present.
- Unknown extra keys inside row objects are tolerated; missing required keys
  cause the import to fail with HTTP 400.
