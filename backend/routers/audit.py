import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import AuditEvent, Evidence, Task, WorkflowProposal

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["Audit"])

@router.get("/audit-log")
def audit_log(project_id: str, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(AuditEvent.project_id == project_id).order_by(AuditEvent.created_at.desc()).all()
    result = []
    for event in events:
        can_undo = False
        if event.event_type == "PROPOSAL_APPROVED" and event.entity_id:
            proposal = db.query(WorkflowProposal).filter(
                WorkflowProposal.id == event.entity_id,
                WorkflowProposal.project_id == project_id,
            ).first()
            if proposal and proposal.status == "APPROVED" and proposal.created_task_id:
                task = db.query(Task).filter(Task.id == proposal.created_task_id).first()
                can_undo = bool(
                    task
                    and task.status == "NOT_STARTED"
                    and not db.query(Evidence).filter(Evidence.task_id == task.id).first()
                )
        result.append({"id": event.id, "event_type": event.event_type, "entity_type": event.entity_type, "entity_id": event.entity_id, "details": json.loads(event.details or "{}"), "created_at": event.created_at, "can_undo": can_undo})
    return result
