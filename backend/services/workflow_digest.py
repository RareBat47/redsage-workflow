from backend.models.schema import Asset, Evidence, Finding, Phase, Task
from backend.services.readiness_service import calculate_phase_coverage


def build_workflow_digest(project_id: str, db) -> dict:
    phases = db.query(Phase).filter(
        Phase.project_id == project_id,
        Phase.is_archived.is_(False),
    ).order_by(Phase.order_index).all()
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_archived.is_(False),
    ).all()
    coverage = calculate_phase_coverage(phases, tasks)
    phase_by_id = {phase.id: phase for phase in phases}
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    asset_counts = {phase.name: 0 for phase in phases}
    unlinked_assets = 0
    for asset in assets:
        task = next((item for item in tasks if item.id == asset.source_task_id), None)
        phase = phase_by_id.get(task.phase_id) if task else None
        if phase:
            asset_counts[phase.name] += 1
        else:
            unlinked_assets += 1

    findings = db.query(Finding).filter(
        Finding.project_id == project_id,
        Finding.status == "CONFIRMED",
    ).all()
    evidence_by_id = {item.id: item for item in db.query(Evidence).filter(Evidence.project_id == project_id).all()}
    finding_counts = {phase.name: 0 for phase in phases}
    unlinked_findings = 0
    finding_summaries = []
    for finding in findings:
        evidence = evidence_by_id.get(finding.evidence_id) if finding.evidence_id else None
        task = next((item for item in tasks if item.id == evidence.task_id), None) if evidence else None
        phase = phase_by_id.get(task.phase_id) if task else None
        if phase:
            finding_counts[phase.name] += 1
        else:
            unlinked_findings += 1
        finding_summaries.append({"title": finding.title, "severity": finding.severity, "phase": phase.name if phase else None})

    phase_rows = []
    for phase in phases:
        phase_tasks = [task for task in tasks if task.phase_id == phase.id]
        phase_rows.append({
            "name": phase.name,
            "order_index": phase.order_index,
            "coverage": coverage.get(phase.name, 0),
            "task_total": len(phase_tasks),
            "task_terminal": sum(task.status in {"COMPLETED", "SKIPPED", "CONFIRMED_NEGATIVE"} for task in phase_tasks),
            "asset_count": asset_counts[phase.name],
            "confirmed_finding_count": finding_counts[phase.name],
        })
    return {
        "project_id": project_id,
        "phases": phase_rows,
        "coverage": coverage,
        "asset_count": len(assets),
        "unlinked_asset_count": unlinked_assets,
        "confirmed_finding_count": len(findings),
        "unlinked_finding_count": unlinked_findings,
        "evidence_count": len(evidence_by_id),
        "confirmed_findings": finding_summaries,
    }
