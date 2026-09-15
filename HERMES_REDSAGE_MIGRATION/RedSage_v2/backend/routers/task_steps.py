import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import Scope, Task, TaskStep
from backend.schemas.api_schemas import EvidenceSubmit, TaskStepCreate, TaskStepUpdate
from backend.services.audit_service import record_event
from backend.routers.evidence import verify_and_persist_evidence
from backend.services.task_state import StateTransitionError, active_steps, rollup_task_from_steps, validate_state_transition


router = APIRouter(prefix="/api/v1/projects/{project_id}/tasks/{task_id}/steps", tags=["Task Steps"])


def get_task(project_id: str, task_id: str, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


def get_step(project_id: str, task_id: str, step_id: str, db: Session) -> tuple[Task, TaskStep]:
    task = get_task(project_id, task_id, db)
    step = db.query(TaskStep).filter(TaskStep.id == step_id, TaskStep.task_id == task.id).first()
    if not step:
        raise HTTPException(404, "Step not found")
    return task, step


def step_dict(step: TaskStep) -> dict:
    return {
        "id": step.id,
        "task_id": step.task_id,
        "title": step.title,
        "objective": step.objective,
        "why_it_matters": step.why_it_matters,
        "completion_criteria": step.completion_criteria,
        "expected_evidence_type": step.expected_evidence_type,
        "status": step.status,
        "order_index": step.order_index,
        "is_ai_proposed": step.is_ai_proposed,
        "is_archived": step.is_archived,
        "archived_at": step.archived_at,
        "archived_by": step.archived_by,
        "justification": step.justification,
    }


@router.get("")
def list_steps(project_id: str, task_id: str, db: Session = Depends(get_db)):
    task = get_task(project_id, task_id, db)
    return [step_dict(step) for step in active_steps(task, db)]


@router.post("")
def create_step(project_id: str, task_id: str, payload: TaskStepCreate, db: Session = Depends(get_db)):
    task = get_task(project_id, task_id, db)
    if task.status == "COMPLETED":
        raise HTTPException(409, "Cannot add steps to a completed task")
    siblings = active_steps(task, db)
    step = TaskStep(
        id=str(uuid.uuid4()),
        task_id=task.id,
        title=payload.title.strip(),
        objective=payload.objective.strip(),
        why_it_matters=payload.why_it_matters.strip(),
        completion_criteria=payload.completion_criteria.strip(),
        expected_evidence_type=payload.expected_evidence_type.strip() or "TERMINAL_LOG",
        order_index=(siblings[-1].order_index + 1) if siblings else 1,
        is_ai_proposed=False,
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step_dict(step)


@router.put("/{step_id}")
def update_step(project_id: str, task_id: str, step_id: str, payload: TaskStepUpdate, db: Session = Depends(get_db)):
    _task, step = get_step(project_id, task_id, step_id, db)
    if step.is_archived:
        raise HTTPException(409, "Archived steps cannot be edited")
    step.title = payload.title.strip()
    step.objective = payload.objective.strip()
    step.why_it_matters = payload.why_it_matters.strip()
    step.completion_criteria = payload.completion_criteria.strip()
    step.expected_evidence_type = payload.expected_evidence_type.strip() or "TERMINAL_LOG"
    if payload.order_index is not None:
        step.order_index = payload.order_index
    db.commit()
    db.refresh(step)
    return step_dict(step)


@router.post("/{step_id}/state")
def update_step_state(project_id: str, task_id: str, step_id: str, payload: dict, db: Session = Depends(get_db)):
    task, step = get_step(project_id, task_id, step_id, db)
    if step.is_archived:
        raise HTTPException(409, "Archived steps cannot change state")
    status = payload.get("status")
    justification = payload.get("justification")
    try:
        validate_state_transition(status, justification)
    except StateTransitionError as error:
        raise HTTPException(error.status_code, str(error)) from error
    previous_status = step.status
    step.status = status
    step.justification = justification
    record_event(db, project_id, "TASK_STATE_CHANGED", "task_step", step.id, {"from": previous_status, "to": status, "justification": justification or ""})
    rollup_task_from_steps(task, project_id, db)
    db.commit()
    return {"status": "success", "step_status": step.status, "task_status": task.status}


@router.post("/{step_id}/verify")
def verify_step(
    project_id: str,
    task_id: str,
    step_id: str,
    payload: EvidenceSubmit,
    db: Session = Depends(get_db),
):
    scope = db.query(Scope).filter(Scope.project_id == project_id).first()
    task, step = get_step(project_id, task_id, step_id, db)
    if not scope or not scope.is_locked:
        raise HTTPException(400, "Cannot verify evidence while scope is unlocked")
    if step.is_archived:
        raise HTTPException(409, "Archived steps cannot be verified")
    return verify_and_persist_evidence(project_id, task, payload.raw_content.strip(), db, step=step)
