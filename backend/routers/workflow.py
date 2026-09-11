from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import Project
from backend.schemas.api_schemas import WorkflowApply
from backend.services.audit_service import record_event
from backend.services.planner_service import WorkflowDraft, generate_workflow
from backend.services.workflow_engine import archive_active_workflow, insert_workflow_draft


router = APIRouter(prefix="/api/v1/projects/{project_id}/workflow", tags=["Workflow"])


@router.post("/generate")
def generate_project_workflow(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return generate_workflow(project.brief or "")


@router.post("/apply")
def apply_project_workflow(project_id: str, payload: WorkflowApply, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    try:
        draft = WorkflowDraft.model_validate(payload.draft)
        if payload.mode == "replace":
            archive_active_workflow(project_id, db)
        insert_workflow_draft(project_id, draft, db, merge=payload.mode == "merge")
        record_event(
            db,
            project_id,
            "WORKFLOW_REPLACED" if payload.mode == "replace" else "WORKFLOW_MERGED",
            "workflow",
            project_id,
            {"mode": payload.mode, "phase_count": len(draft.phases)},
        )
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(422, str(error)) from error
    except Exception:
        db.rollback()
        raise
    return {"status": "applied", "mode": payload.mode, "phase_count": len(draft.phases)}
