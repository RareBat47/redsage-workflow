from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Finding, Phase, Project, Task, WorkflowProposal, Evidence
from backend.services.report_builder import build_markdown_report
from backend.services.report_data import load_report_context
from backend.services.readiness_service import calculate_phase_coverage

router=APIRouter(prefix="/api/v1/projects/{project_id}/report",tags=["Reporting"])

def report(project_id, db):
    context = load_report_context(db, project_id)
    if not context:
        raise HTTPException(404,"Project not found")
    project, scope, tasks, findings, assets, evidence, amendments = context
    return build_markdown_report(project, scope, tasks, findings, assets, evidence, amendments)

@router.get("")
def preview(project_id: str, db: Session=Depends(get_db)): return {"markdown":report(project_id,db)}
@router.get("/download")
def download(project_id: str, db: Session=Depends(get_db)):
    project=db.query(Project).filter(Project.id==project_id).first(); md=report(project_id,db)
    return Response(md,media_type="text/markdown",headers={"Content-Disposition":f'attachment; filename="redsage_report_{project.name.lower().replace(" ","_")}.md"'})

@router.get("/readiness")
def readiness(project_id: str, db: Session = Depends(get_db)):
    issues = []
    findings = db.query(Finding).filter(Finding.project_id == project_id, Finding.status == "CONFIRMED").all()
    for finding in findings:
        evidence = db.query(Evidence).filter(Evidence.id == finding.evidence_id, Evidence.project_id == project_id).first() if finding.evidence_id else None
        if not evidence:
            issues.append({"severity":"CRITICAL","message":f'Finding "{finding.title}" is missing linked evidence.',"entity_type":"finding","entity_id":finding.id})
        if not (finding.reproduction_steps or "").strip():
            issues.append({"severity":"WARNING","message":f'Finding "{finding.title}" is missing reproduction steps.',"entity_type":"finding","entity_id":finding.id})
        if not (finding.remediation or "").strip():
            issues.append({"severity":"WARNING","message":f'Finding "{finding.title}" is missing remediation advice.',"entity_type":"finding","entity_id":finding.id})
    tasks = db.query(Task).filter(Task.project_id == project_id, Task.is_archived.is_(False)).all()
    for task in tasks:
        if task.status in ["SKIPPED", "CONFIRMED_NEGATIVE"] and len((task.justification or "").strip()) < 10:
            issues.append({"severity":"WARNING","message":f'Task "{task.title}" requires a detailed justification.',"entity_type":"task","entity_id":task.id})
    pending = db.query(WorkflowProposal).filter(WorkflowProposal.project_id == project_id, WorkflowProposal.status == "PENDING").count()
    if pending:
        issues.append({"severity":"INFO","message":f"{pending} workflow proposals remain unreviewed.","entity_type":"proposal","entity_id":None})
    phases = db.query(Phase).filter(Phase.project_id == project_id, Phase.is_archived.is_(False)).order_by(Phase.order_index).all()
    coverage = calculate_phase_coverage(phases, tasks)
    critical = sum(issue["severity"] == "CRITICAL" for issue in issues)
    warnings = sum(issue["severity"] == "WARNING" for issue in issues)
    score = max(0, 100 - critical * 30 - warnings * 10)
    return {"ready_for_export": critical == 0, "score": score, "issues": issues, "coverage": coverage}
