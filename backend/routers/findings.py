import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Evidence, Finding
from backend.schemas.api_schemas import FindingConfirm, FindingCreate
from backend.services.audit_service import record_event

router = APIRouter(prefix="/api/v1/projects/{project_id}/findings", tags=["Findings"])

ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "INFO"}

def finding_dict(finding: Finding) -> dict:
    return {
        "id": finding.id,
        "project_id": finding.project_id,
        "title": finding.title,
        "severity": finding.severity,
        "status": finding.status,
        "affected_asset": finding.affected_asset,
        "description": finding.description,
        "reproduction_steps": finding.reproduction_steps,
        "remediation": finding.remediation,
        "evidence_id": finding.evidence_id,
    }

@router.get("")
def list_findings(project_id: str, db: Session = Depends(get_db)):
    return [finding_dict(finding) for finding in db.query(Finding).filter(Finding.project_id == project_id).all()]

@router.post("")
def create_finding(project_id: str, payload: FindingCreate, db: Session = Depends(get_db)):
    # DRAFT is the default lifecycle state. Evidence is optional here, but if a
    # draft references evidence it must belong to this project so the register
    # never carries dangling cross-project references.
    if payload.evidence_id and not db.query(Evidence).filter(
        Evidence.id == payload.evidence_id, Evidence.project_id == project_id
    ).first():
        raise HTTPException(400, "Cannot link draft finding to unknown evidence in this project")
    finding = Finding(
        id=str(uuid.uuid4()),
        project_id=project_id,
        title=payload.title,
        severity=payload.severity or "MEDIUM",
        status="DRAFT",
        affected_asset=payload.affected_asset,
        description=payload.description or "",
        reproduction_steps=payload.reproduction_steps or "",
        remediation=payload.remediation,
        evidence_id=payload.evidence_id,
    )
    db.add(finding)
    db.flush()
    record_event(db, project_id, "FINDING_DRAFTED", "finding", finding.id, {"title": finding.title, "has_evidence": bool(finding.evidence_id)})
    db.commit()
    return {"status": "drafted", "finding_id": finding.id}

@router.post("/{finding_id}/confirm")
def confirm_finding(project_id: str, finding_id: str, payload: FindingConfirm, db: Session = Depends(get_db)):
    finding = db.query(Finding).filter(Finding.id == finding_id, Finding.project_id == project_id).first()
    if not finding:
        raise HTTPException(404, "Finding not found")
    if finding.status == "CONFIRMED":
        raise HTTPException(400, "Finding is already confirmed")
    for field in ("title", "severity", "description", "reproduction_steps", "remediation", "affected_asset"):
        value = getattr(payload, field)
        if value is not None:
            setattr(finding, field, value)
    finding.evidence_id = payload.evidence_id
    evidence = db.query(Evidence).filter(Evidence.id == finding.evidence_id, Evidence.project_id == project_id).first()
    if not evidence:
        raise HTTPException(422, "Cannot confirm finding without valid linked evidence in this project")
    missing = [name for name in ("title", "severity", "description", "reproduction_steps") if not (getattr(finding, name) or "").strip()]
    if finding.severity and finding.severity.strip().upper() not in ALLOWED_SEVERITIES:
        missing.append("severity (must be LOW, MEDIUM, HIGH, CRITICAL, or INFO)")
    if missing:
        raise HTTPException(422, f"Cannot confirm finding; missing or invalid: {', '.join(missing)}")
    finding.severity = finding.severity.strip().upper()
    finding.status = "CONFIRMED"
    record_event(db, project_id, "FINDING_CONFIRMED", "finding", finding.id, {"evidence_id": finding.evidence_id, "severity": finding.severity})
    db.commit()
    return {"status": "confirmed", "finding_id": finding.id}
