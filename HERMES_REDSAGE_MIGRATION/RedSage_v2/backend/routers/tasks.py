import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Phase, Scope, Task, TaskStep
from backend.schemas.api_schemas import TaskStateUpdate
from backend.services.scope_validator import is_target_in_scope, is_target_whitelisted
from backend.services.audit_service import record_event
from backend.services.task_state import StateTransitionError, active_steps, validate_state_transition

router=APIRouter(prefix="/api/v1/projects/{project_id}/tasks", tags=["Tasks"])

def resolve_active_target(scope, target_host: str | None) -> str:
    """Pick the target used for command resolution and scope-safety checks.

    An explicit target_host must be covered by the project whitelist (exact
    entries, ``*.`` wildcard entries, and CIDR ranges all count); otherwise the
    request is rejected so commands can never be resolved for out-of-scope
    hosts. Without a selection the first concrete (non-wildcard) whitelist
    entry remains the default (legacy behavior). A wildcard-only whitelist has
    no concrete default, so commands stay unresolved (TARGET_UNSPECIFIED)
    until the analyst picks a specific host.
    """
    whitelist = json.loads(scope.in_scope_whitelist) if scope else []
    if target_host is not None and target_host.strip():
        normalized = target_host.strip()
        if not is_target_whitelisted(normalized, whitelist):
            raise HTTPException(422, "target_host is not within the project scope whitelist")
        return normalized
    for entry in whitelist:
        candidate = entry.strip()
        if candidate and not candidate.startswith("*."):
            return candidate
    return "TARGET_UNSPECIFIED"

@router.get("")
def list_tasks(project_id: str, target_host: str | None = None, db: Session=Depends(get_db)):
    scope=db.query(Scope).filter(Scope.project_id==project_id).first(); whitelist=json.loads(scope.in_scope_whitelist) if scope else []; blacklist=json.loads(scope.out_of_scope_blacklist) if scope else []; target=resolve_active_target(scope, target_host)
    result=[]
    for phase in db.query(Phase).filter(Phase.project_id==project_id, Phase.is_archived.is_(False)).order_by(Phase.order_index):
        tasks=[]
        for task in sorted((item for item in phase.tasks if not item.is_archived),key=lambda item:item.order_index):
            resolved=task.command_template.replace("{target_host}",target).replace("{rate_limit}",str(scope.max_rate_limit if scope else 10)) if task.command_template else None
            tasks.append({"id":task.id,"phase_id":task.phase_id,"title":task.title,"objective":task.objective,"command_template":task.command_template,"resolved_command":resolved,"is_scope_safe":bool(scope and scope.is_locked and is_target_in_scope(target,whitelist,blacklist)),"status":task.status,"priority":task.priority,"order_index":task.order_index,"is_ai_proposed":task.is_ai_proposed,"justification":task.justification,"steps":[{"id":step.id,"title":step.title,"status":step.status,"order_index":step.order_index,"is_archived":step.is_archived} for step in active_steps(task, db)]})
        result.append({"id":phase.id,"name":phase.name,"order_index":phase.order_index,"tasks":tasks})
    return result
@router.post("/{task_id}/state")
def update_task_state(project_id:str,task_id:str,payload:TaskStateUpdate,db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id,Task.project_id==project_id).first()
    if not task: raise HTTPException(404,"Task not found")
    status=payload.status; justification=payload.justification
    if status == "COMPLETED" and active_steps(task, db) and any(step.status not in {"COMPLETED", "SKIPPED", "CONFIRMED_NEGATIVE"} for step in active_steps(task, db)):
        raise HTTPException(409, "Task completion is controlled by its active steps")
    try:
        validate_state_transition(status, justification)
    except StateTransitionError as error:
        raise HTTPException(error.status_code, str(error)) from error
    previous_status = task.status
    task.status=status; task.justification=justification; record_event(db, project_id, "TASK_STATE_CHANGED", "task", task.id, {"from": previous_status, "to": status, "justification": justification or ""}); db.commit(); return {"status":"success","task_status":task.status}
