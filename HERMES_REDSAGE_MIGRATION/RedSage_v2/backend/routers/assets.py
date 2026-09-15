import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Asset, Task, WorkflowProposal
from backend.services.asset_proposal_service import suggest_safe_tasks, workflow_context

router = APIRouter(prefix="/api/v1/projects/{project_id}/assets", tags=["Assets"])

@router.get("")
def list_assets(project_id: str, db: Session = Depends(get_db)):
    assets = db.query(Asset).filter(Asset.project_id == project_id).order_by(Asset.type, Asset.value).all()
    rows = []
    for asset in assets:
        task = db.query(Task).filter(Task.id == asset.source_task_id).first() if asset.source_task_id else None
        rows.append({"id": asset.id, "type": asset.type, "value": asset.value, "source_task": task.title if task else "Evidence-derived", "source_task_id": asset.source_task_id})
    return rows

@router.post("/{asset_id}/suggest-tasks")
def suggest_tasks(project_id: str, asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.project_id == project_id).first()
    if not asset: raise HTTPException(404, "Asset not found")
    pending_count = db.query(WorkflowProposal).filter(WorkflowProposal.project_id == project_id, WorkflowProposal.status == "PENDING").count()
    if pending_count >= 5: raise HTTPException(400, "Review pending proposals before requesting more")
    duplicate = db.query(WorkflowProposal).filter(WorkflowProposal.project_id == project_id, WorkflowProposal.target_asset == asset.value, WorkflowProposal.action_type == "ASSET_REVIEW").first()
    if duplicate: return {"status": "deduplicated", "created_count": 0}
    proposals = suggest_safe_tasks(asset.type, asset.value, workflow_context(db, project_id))[:max(0, 5 - pending_count)]
    created = 0
    existing_titles = {title for (title,) in db.query(Task.title).filter(Task.project_id == project_id).all()}
    existing_titles.update(title for (title,) in db.query(WorkflowProposal.title).filter(WorkflowProposal.project_id == project_id).all())
    for item in proposals:
        if item.title in existing_titles: continue
        db.add(WorkflowProposal(id=str(uuid.uuid4()), project_id=project_id, phase_name=item.phase_name, title=item.title, objective=item.objective, priority=item.priority, target_asset=asset.value, action_type="ASSET_REVIEW", status="PENDING"))
        created += 1
    db.commit()
    return {"status": "proposed", "created_count": created}
