import json


def build_markdown_report(project, scope, tasks, findings, assets, evidence=None, amendments=None) -> str:
    """Build a traceable Markdown report without reading raw artifact contents."""
    evidence = evidence or []
    amendments = amendments or []
    whitelist = json.loads(scope.in_scope_whitelist) if scope else []
    blacklist = json.loads(scope.out_of_scope_blacklist) if scope else []
    evidence_by_id = {item.id: item for item in evidence}
    lines = [
        f"# Penetration Testing Engagement Report: {project.name}",
        "",
        "## 1. Executive Summary & Posture Overview",
        f"Assessment status: **{project.status}**. The engagement contains {len(tasks)} tracked tasks, {len(assets)} discovered assets, and {sum(1 for item in findings if item.status == 'CONFIRMED')} confirmed findings.",
        "",
        "## 2. Scope & Rules of Engagement Attestation",
        f"- **In-Scope Targets:** {', '.join(f'`{item}`' for item in whitelist) or 'None'}",
        f"- **Excluded Targets:** {', '.join(f'`{item}`' for item in blacklist) or 'None'}",
        f"- **Rate Limit:** {scope.max_rate_limit if scope else 10} requests/second",
        f"- **Scope Authorization Status:** {'LOCKED & ENFORCED' if scope and scope.is_locked else 'UNLOCKED'}",
        "",
        "### 1.1 Authorized Scope Amendments",
        "| Date | Added Targets | Authorized By | Rationale |",
        "|---|---|---|---|",
    ]
    if amendments:
        for amendment in amendments:
            date = amendment.created_at.strftime("%Y-%m-%d %H:%M:%S") if amendment.created_at else "Unknown"
            lines.append(f"| {date} UTC | {', '.join(json.loads(amendment.added_targets))} | {amendment.authorized_by} | {amendment.rationale} |")
    else:
        lines.append("| _None_ | - | - | - |")
    lines.extend([
        "",
        "## 3. Assessment Methodology & Task Execution Matrix",
        "| Task | Status | Priority |",
        "|---|---|---|",
    ])
    lines.extend(f"| {task.title} | `{task.status}` | {task.priority} |" for task in tasks)
    lines.extend(["", "## 4. Target Asset Inventory"])
    if assets:
        lines.extend(f"- `{asset.type}`: `{asset.value}`" for asset in assets)
    else:
        lines.append("_No structured assets extracted during testing._")
    lines.extend(["", "## 5. Confirmed Findings"])
    confirmed = [item for item in findings if item.status == "CONFIRMED"]
    if not confirmed:
        lines.append("_No security vulnerabilities confirmed during this assessment._")
    for index, finding in enumerate(confirmed, 1):
        lines.extend([
            f"### 5.{index} {finding.title} [{finding.severity.upper()}]",
            f"- **Affected Asset:** `{finding.affected_asset or 'N/A'}`",
            f"- **Evidence Ref: {finding.evidence_id or 'MISSING'}**",
            f"- **CWE:** Not provided",
            f"- **CVSS:** Not provided",
            "",
            finding.description,
            "",
            "#### Reproduction Steps",
            "```text",
            finding.reproduction_steps,
            "```",
        ])
        if finding.evidence_id not in evidence_by_id:
            lines.append("**Readiness warning:** The referenced evidence artifact is missing from this project register.")
        if finding.remediation:
            lines.extend(["", "#### Remediation", finding.remediation])
        lines.append("")
    lines.extend([
        "## Appendix: Evidence Register & Integrity Log",
        "",
        "| Evidence ID | Source Task | Artifact File | File Size | SHA-256 Digest | Timestamp (UTC) |",
        "|---|---|---|---:|---|---|",
    ])
    if evidence:
        for item in evidence:
            task_title = item.task.title if item.task else item.task_id
            filename = item.file_path.rsplit("/", 1)[-1] if item.file_path else "MISSING"
            timestamp = item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "Unknown"
            lines.append(f"| `{item.id}` | {task_title} | `{filename}` | {item.file_size_bytes} B | `{item.sha256_hash}` | {timestamp} UTC |")
    else:
        lines.append("| _None_ | - | - | 0 B | - | - |")
    return "\n".join(lines) + "\n"
