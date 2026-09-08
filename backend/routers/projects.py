import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Project, Scope
from backend.schemas.api_schemas import ProjectCreate
from backend.services.workflow_engine import seed_project_tasks

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

def project_dict(project):
    return {"id": project.id, "name": project.name, "description": project.description, "target_type": project.target_type, "status": project.status, "created_at": project.created_at}

@router.get("")
def list_projects(db: Session = Depends(get_db)):
    return [project_dict(project) for project in db.query(Project).order_by(Project.created_at.desc()).all()]

@router.post("")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(id=str(uuid.uuid4()), name=payload.name, description=payload.description, target_type=payload.target_type)
    db.add(project)
    db.add(Scope(id=str(uuid.uuid4()), project_id=project.id, in_scope_whitelist=json.dumps([]), out_of_scope_blacklist=json.dumps([]), max_rate_limit=10))
    db.commit()
    seed_project_tasks(project.id, db)
    return project_dict(project)

@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project_dict(project)
