import datetime
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Scope, ScopeAmendment
from backend.schemas.api_schemas import ScopeAmend, ScopeUpdate
from backend.services.scope_validator import is_valid_target
from backend.services.audit_service import record_event

router = APIRouter(prefix="/api/v1/projects/{project_id}/scope", tags=["Scope"])

def get_scope_or_404(project_id, db):
    scope = db.query(Scope).filter(Scope.project_id == project_id).first()
    if not scope: raise HTTPException(404, "Scope not found")
    return scope

@router.get("")
def get_scope(project_id: str, db: Session = Depends(get_db)):
    scope = get_scope_or_404(project_id, db)
    return {"id":scope.id,"project_id":scope.project_id,"in_scope_whitelist":json.loads(scope.in_scope_whitelist),"out_of_scope_blacklist":json.loads(scope.out_of_scope_blacklist),"max_rate_limit":scope.max_rate_limit,"is_locked":scope.is_locked,"locked_at":scope.locked_at}

@router.put("")
def update_scope(project_id: str, payload: ScopeUpdate, db: Session = Depends(get_db)):
    scope = get_scope_or_404(project_id, db)
    if scope.is_locked: raise HTTPException(400, "Scope is locked and cannot be modified directly")
    if not payload.in_scope_whitelist or any(not is_valid_target(target) for target in payload.in_scope_whitelist):
        raise HTTPException(422, "Invalid domain/IP format in whitelist")
    if any(not is_valid_target(target) for target in payload.out_of_scope_blacklist):
        raise HTTPException(422, "Invalid domain/IP format in blacklist")
    scope.in_scope_whitelist=json.dumps(payload.in_scope_whitelist); scope.out_of_scope_blacklist=json.dumps(payload.out_of_scope_blacklist); scope.max_rate_limit=payload.max_rate_limit
    db.commit(); return {"status":"updated"}

@router.post("/lock")
def lock_scope(project_id: str, db: Session = Depends(get_db)):
    scope = get_scope_or_404(project_id, db)
    if not json.loads(scope.in_scope_whitelist): raise HTTPException(400, "Cannot lock scope without at least one in-scope target")
    scope.is_locked=True; scope.locked_at=datetime.datetime.utcnow(); record_event(db, project_id, "SCOPE_LOCKED", "scope", scope.id, {"targets": json.loads(scope.in_scope_whitelist)}); db.commit()
    return {"status":"locked", "locked_at":scope.locked_at}

@router.post("/amend")
def amend_scope(project_id: str, payload: ScopeAmend, db: Session = Depends(get_db)):
    scope = get_scope_or_404(project_id, db)
    if not scope.is_locked:
        raise HTTPException(400, "Scope must be locked before it can be amended")
    targets = [str(target).strip() for target in payload.additional_targets if str(target).strip()]
    authorized_by = payload.authorized_by.strip()
    rationale = payload.rationale.strip()
    if not targets or any(not is_valid_target(target) for target in targets):
        raise HTTPException(422, "Every additional target must be a valid domain or IP")
    if not authorized_by:
        raise HTTPException(422, "authorized_by is required")
    if len(rationale) < 10:
        raise HTTPException(422, "rationale must be at least 10 characters")
    current = json.loads(scope.in_scope_whitelist)
    additions = [target for target in targets if target.lower() not in {item.lower() for item in current}]
    if not additions:
        raise HTTPException(400, "All additional targets are already in scope")
    scope.in_scope_whitelist = json.dumps(current + additions)
    amendment = ScopeAmendment(id=str(uuid.uuid4()), project_id=project_id, added_targets=json.dumps(additions), authorized_by=authorized_by, rationale=rationale)
    db.add(amendment)
    record_event(db, project_id, "SCOPE_AMENDED", "scope_amendment", amendment.id, {"added_targets": additions, "authorized_by": authorized_by, "rationale": rationale})
    db.commit()
    return {"status": "amended", "added_targets": additions, "amendment_id": amendment.id}
