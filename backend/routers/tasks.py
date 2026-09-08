import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Phase, Scope, Task
from backend.services.scope_validator import is_target_in_scope
from backend.services.audit_service import record_event

router=APIRouter(prefix="/api/v1/projects/{project_id}/tasks", tags=["Tasks"])

def resolve_active_target(scope, target_host: str | None) -> str:
    """Pick the target used for command resolution and scope-safety checks.

    An explicit target_host must be whitelisted for this project; otherwise the
    request is rejected so commands can never be resolved for out-of-scope
    hosts. Without a selection the first whitelist entry remains the default
    (legacy behavior).
    """
    whitelist = json.loads(scope.in_scope_whitelist) if scope else []
    if target_host is not None and target_host.strip():
        normalized = target_host.strip()
        if normalized.lower() not in {item.strip().lower() for item in whitelist}:
            raise HTTPException(422, "target_host is not within the project scope whitelist")
        return normalized
    return whitelist[0] if whitelist else "TARGET_UNSPECIFIED"

@router.get("")
def list_tasks(project_id: str, target_host: str | None = None, db: Session=Depends(get_db)):
    scope=db.query(Scope).filter(Scope.project_id==project_id).first(); whitelist=json.loads(scope.in_scope_whitelist) if scope else []; blacklist=json.loads(scope.out_of_scope_blacklist) if scope else []; target=resolve_active_target(scope, target_host)
    result=[]
    for phase in db.query(Phase).filter(Phase.project_id==project_id).order_by(Phase.order_index):
        tasks=[]
        for task in sorted(phase.tasks,key=lambda item:item.order_index):
            resolved=task.command_template.replace("{target_host}",target).replace("{rate_limit}",str(scope.max_rate_limit if scope else 10)) if task.command_template else None
            tasks.append({"id":task.id,"phase_id":task.phase_id,"title":task.title,"objective":task.objective,"command_template":task.command_template,"resolved_command":resolved,"is_scope_safe":bool(scope and scope.is_locked and is_target_in_scope(target,whitelist,blacklist)),"status":task.status,"priority":task.priority,"order_index":task.order_index,"is_ai_proposed":task.is_ai_proposed,"justification":task.justification})
        result.append({"id":phase.id,"name":phase.name,"order_index":phase.order_index,"tasks":tasks})
    return result
@router.post("/{task_id}/state")
def update_task_state(project_id:str,task_id:str,payload:dict,db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id,Task.project_id==project_id).first()
    if not task: raise HTTPException(404,"Task not found")
    status=payload.get("status"); justification=payload.get("justification")
    if status in ["SKIPPED","CONFIRMED_NEGATIVE"] and len((justification or "").strip())<5: raise HTTPException(400,"Justification required")
    if status not in ["NOT_STARTED","IN_PROGRESS","COMPLETED","SKIPPED","CONFIRMED_NEGATIVE"]: raise HTTPException(422,"Invalid task status")
    previous_status = task.status
    task.status=status; task.justification=justification; record_event(db, project_id, "TASK_STATE_CHANGED", "task", task.id, {"from": previous_status, "to": status, "justification": justification or ""}); db.commit(); return {"status":"success","task_status":task.status}
