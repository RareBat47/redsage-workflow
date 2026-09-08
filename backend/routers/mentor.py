import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import Scope, Task
from backend.schemas.api_schemas import MentorAsk
from backend.services.audit_service import record_event
from backend.services.mentor_service import ask_mentor, build_context_pack

router = APIRouter(prefix="/api/v1/projects/{project_id}/tasks/{task_id}/mentor", tags=["Mentor"])


@router.post("")
def ask_task_mentor(project_id: str, task_id: str, payload: MentorAsk, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    target = None
    if payload.target_host and payload.target_host.strip():
        scope = db.query(Scope).filter(Scope.project_id == project_id).first()
        whitelist = json.loads(scope.in_scope_whitelist) if scope else []
        if payload.target_host.strip().lower() not in {item.strip().lower() for item in whitelist}:
            raise HTTPException(422, "target_host is not within the project scope whitelist")
        target = payload.target_host.strip()
    context = build_context_pack(project_id, task, db, target)
    reply = ask_mentor(payload.mode, payload.user_message, context)
    # The analyst's message content is deliberately not recorded; only mode,
    # availability, and length enter the audit trail.
    record_event(db, project_id, "MENTOR_ASKED", "task", task.id, {
        "mode": payload.mode,
        "ai_available": reply.ai_available,
        "question_chars": len(payload.user_message),
    })
    db.commit()
    return {"mode": reply.mode, "reply": reply.reply, "ai_available": reply.ai_available}
