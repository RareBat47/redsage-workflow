from types import SimpleNamespace

from backend.services.report_builder import build_markdown_report


def test_report_contains_evidence_register_and_finding_reference():
    project = SimpleNamespace(name="Trace Test", status="IN_PROGRESS")
    scope = SimpleNamespace(in_scope_whitelist="[\"target.local\"]", out_of_scope_blacklist="[]", max_rate_limit=10, is_locked=True)
    task = SimpleNamespace(title="Evidence task", status="COMPLETED", priority="HIGH")
    evidence = SimpleNamespace(id="EVID-001", task_id="task-1", task=task, file_path="data/projects/p/artifacts/EVID-001.txt", file_size_bytes=12, sha256_hash="a" * 64, created_at=None)
    finding = SimpleNamespace(title="Test finding", severity="HIGH", affected_asset="target.local", evidence_id="EVID-001", description="Description", reproduction_steps="Steps", remediation=None, status="CONFIRMED")
    report = build_markdown_report(project, scope, [task], [finding], [], [evidence])
    assert "Evidence Register & Integrity Log" in report
    assert "Evidence Ref: EVID-" in report
    assert "EVID-001" in report


def test_report_warns_for_missing_finding_evidence():
    project = SimpleNamespace(name="Trace Test", status="IN_PROGRESS")
    scope = SimpleNamespace(in_scope_whitelist="[]", out_of_scope_blacklist="[]", max_rate_limit=10, is_locked=False)
    finding = SimpleNamespace(title="Missing evidence", severity="LOW", affected_asset=None, evidence_id="EVID-MISSING", description="Description", reproduction_steps="Steps", remediation=None, status="CONFIRMED")
    report = build_markdown_report(project, scope, [], [finding], [], [])
    assert "readiness warning" in report.lower()
