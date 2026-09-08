from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schema import Asset, Evidence, Finding

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["Search"])

@router.get("/search")
def project_search(project_id: str, q: str = Query(min_length=1, max_length=200), db: Session = Depends(get_db)):
    pattern = f"%{q.strip()}%"
    findings = db.query(Finding).filter(Finding.project_id == project_id, or_(Finding.title.ilike(pattern), Finding.description.ilike(pattern))).limit(5).all()
    evidence = db.query(Evidence).filter(Evidence.project_id == project_id, or_(Evidence.id.ilike(pattern), Evidence.redacted_excerpt.ilike(pattern))).limit(5).all()
    assets = db.query(Asset).filter(Asset.project_id == project_id, Asset.value.ilike(pattern)).limit(5).all()
    return {"findings":[{"id":item.id,"title":item.title,"snippet":item.description[:180],"target_view":"roadmap"} for item in findings],"evidence":[{"id":item.id,"title":item.id,"snippet":item.redacted_excerpt[:180],"target_view":"evidence"} for item in evidence],"assets":[{"id":item.id,"title":item.value,"snippet":item.type,"target_view":"assets"} for item in assets]}
