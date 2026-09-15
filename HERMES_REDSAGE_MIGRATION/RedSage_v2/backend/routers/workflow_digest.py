import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import MentorMessage, Project
from backend.schemas.api_schemas import MentorAsk
from backend.services.audit_service import record_event
from backend.services.cohere_service import clip_log, redact_sensitive_data
from backend.services.mentor_service import ask_mentor
from backend.services.workflow_digest import build_workflow_digest


router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["Boss Brain"])


@router.get("/workflow/digest")
def workflow_digest(project_id: str, db: Session = Depends(get_db)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(404, "Project not found")
    return build_workflow_digest(project_id, db)


@router.post("/mentor/boss")
def ask_boss(project_id: str, payload: MentorAsk, db: Session = Depends(get_db)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(404, "Project not found")
    digest = build_workflow_digest(project_id, db)
    safe_message = redact_sensitive_data(clip_log(payload.user_message, max_lines=60))
    context = {
        "project_digest": digest,
        "question": safe_message,
        "instruction": "Answer read-only status and prioritization questions using only the measured project data. Never invent progress.",
    }
    reply = ask_mentor(payload.mode, safe_message, context)
    db.add(MentorMessage(id=str(uuid.uuid4()), project_id=project_id, task_id=None, step_id=None, mode=payload.mode, role="user", content=safe_message))
    db.add(MentorMessage(id=str(uuid.uuid4()), project_id=project_id, task_id=None, step_id=None, mode=reply.mode, role="assistant", content=reply.reply, ai_available=reply.ai_available))
    record_event(db, project_id, "MENTOR_ASKED", "project", project_id, {"mode": payload.mode, "ai_available": reply.ai_available, "question_chars": len(payload.user_message)})
    db.commit()
    return {"mode": reply.mode, "reply": reply.reply, "ai_available": reply.ai_available}


@router.get("/mentor/boss/history")
def boss_history(project_id: str, db: Session = Depends(get_db)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(404, "Project not found")
    rows = db.query(MentorMessage).filter(
        MentorMessage.project_id == project_id,
        MentorMessage.task_id.is_(None),
        MentorMessage.step_id.is_(None),
    ).order_by(MentorMessage.created_at, MentorMessage.id).all()
    return [{"id": row.id, "role": row.role, "content": row.content, "mode": row.mode, "ai_available": row.ai_available, "created_at": row.created_at} for row in rows]
