import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import MentorMessage, Scope, Task, TaskStep
from backend.schemas.api_schemas import MentorAsk
from backend.services.audit_service import record_event
from backend.services.cohere_service import clip_log, redact_sensitive_data
from backend.services.mentor_service import ask_mentor, build_context_pack
from backend.services.scope_validator import is_target_whitelisted

router = APIRouter(prefix="/api/v1/projects/{project_id}/tasks/{task_id}/mentor", tags=["Mentor"])


@router.post("")
def ask_task_mentor(project_id: str, task_id: str, payload: MentorAsk, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    step = None
    if payload.step_id:
        step = db.query(TaskStep).filter(
            TaskStep.id == payload.step_id,
            TaskStep.task_id == task.id,
            TaskStep.is_archived.is_(False),
        ).first()
        if not step:
            raise HTTPException(404, "Step not found")
    target = None
    if payload.target_host and payload.target_host.strip():
        scope = db.query(Scope).filter(Scope.project_id == project_id).first()
        whitelist = json.loads(scope.in_scope_whitelist) if scope else []
        if not is_target_whitelisted(payload.target_host, whitelist):
            raise HTTPException(422, "target_host is not within the project scope whitelist")
        target = payload.target_host.strip()
    context = build_context_pack(project_id, task, db, target, payload.step_id)
    reply = ask_mentor(payload.mode, payload.user_message, context)
    safe_user_message = redact_sensitive_data(clip_log(payload.user_message, max_lines=60))
    db.add(MentorMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        task_id=task.id,
        step_id=step.id if step else None,
        mode=payload.mode,
        role="user",
        content=safe_user_message,
    ))
    db.add(MentorMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        task_id=task.id,
        step_id=step.id if step else None,
        mode=reply.mode,
        role="assistant",
        content=reply.reply,
        ai_available=reply.ai_available,
    ))
    # The analyst's message content is deliberately not recorded; only mode,
    # availability, and length enter the audit trail.
    record_event(db, project_id, "MENTOR_ASKED", "task", task.id, {
        "mode": payload.mode,
        "ai_available": reply.ai_available,
        "question_chars": len(payload.user_message),
    })
    db.commit()
    return {"mode": reply.mode, "reply": reply.reply, "ai_available": reply.ai_available}


@router.get("/history")
def mentor_history(project_id: str, task_id: str, step_id: str | None = None, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if step_id:
        step = db.query(TaskStep).filter(TaskStep.id == step_id, TaskStep.task_id == task.id).first()
        if not step:
            raise HTTPException(404, "Step not found")
    rows = db.query(MentorMessage).filter(
        MentorMessage.project_id == project_id,
        MentorMessage.task_id == task.id,
        MentorMessage.step_id == step_id,
    ).order_by(MentorMessage.created_at, MentorMessage.id).all()
    return [{
        "id": row.id,
        "role": row.role,
        "content": row.content,
        "mode": row.mode,
        "ai_available": row.ai_available,
        "created_at": row.created_at,
    } for row in rows]
