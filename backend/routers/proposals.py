import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Evidence, Phase, Task, WorkflowProposal
from backend.services.audit_service import record_event

router = APIRouter(prefix="/api/v1/projects/{project_id}/proposals", tags=["Proposals"])

@router.get("")
def list_proposals(project_id: str, db: Session = Depends(get_db)):
    return db.query(WorkflowProposal).filter(WorkflowProposal.project_id == project_id, WorkflowProposal.status == "PENDING").all()

def change_proposal(project_id, proposal_id, status, db):
    proposal = db.query(WorkflowProposal).filter(WorkflowProposal.id == proposal_id, WorkflowProposal.project_id == project_id).first()
    if not proposal: raise HTTPException(404, "Proposal not found")
    if status == "APPROVED":
        phase = db.query(Phase).filter(Phase.project_id == project_id, Phase.name.like("%Phase 4%")).first()
        if not phase: raise HTTPException(400, "No Phase 4 is available for proposed tasks")
        count = db.query(Task).filter(Task.phase_id == phase.id).count()
        task = Task(id=str(uuid.uuid4()), phase_id=phase.id, project_id=project_id, title=proposal.title, objective=proposal.objective, command_template="curl -i https://{target_host}/" + proposal.target_asset.lstrip("/"), priority=proposal.priority, order_index=count + 1, is_ai_proposed=True)
        db.add(task); db.flush(); proposal.status = status; proposal.created_task_id = task.id
        record_event(db, project_id, "PROPOSAL_APPROVED", "proposal", proposal.id, {"task_id": task.id, "target_asset": proposal.target_asset})
        db.commit(); return {"status":"approved", "task_id":task.id}
    proposal.status = status; db.commit(); return {"status":"dismissed"}

@router.post("/{proposal_id}/approve")
def approve(project_id: str, proposal_id: str, db: Session = Depends(get_db)): return change_proposal(project_id, proposal_id, "APPROVED", db)

@router.post("/{proposal_id}/dismiss")
def dismiss(project_id: str, proposal_id: str, db: Session = Depends(get_db)): return change_proposal(project_id, proposal_id, "DISMISSED", db)

@router.post("/{proposal_id}/undo")
def undo(project_id: str, proposal_id: str, db: Session = Depends(get_db)):
    proposal = db.query(WorkflowProposal).filter(WorkflowProposal.id == proposal_id, WorkflowProposal.project_id == project_id).first()
    if not proposal or proposal.status != "APPROVED" or not proposal.created_task_id:
        raise HTTPException(400, "Proposal has no eligible approved task to undo")
    task = db.query(Task).filter(Task.id == proposal.created_task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(400, "Approved task no longer exists")
    if task.status != "NOT_STARTED" or db.query(Evidence).filter(Evidence.task_id == task.id).first():
        raise HTTPException(400, "Only untouched proposed tasks can be undone")
    task_id = task.id
    db.delete(task); proposal.status = "PENDING"; proposal.created_task_id = None
    record_event(db, project_id, "PROPOSAL_UNDONE", "proposal", proposal.id, {"task_id": task_id})
    db.commit()
    return {"status": "undone", "proposal_id": proposal.id}
