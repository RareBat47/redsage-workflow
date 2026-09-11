from __future__ import annotations

from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import Asset, Evidence, Scope, Task, TaskStep, WorkflowProposal
from backend.schemas.api_schemas import EvidenceSubmit
from backend.services.artifact_manager import read_artifact, save_artifact
from backend.services.cohere_service import create_safe_excerpt, verify_task_evidence
from backend.services.audit_service import record_event
from backend.services.task_state import active_steps, rollup_task_from_steps
from backend.services.asset_proposal_service import DEFAULT_PHASE, suggest_safe_tasks, workflow_context

router = APIRouter(tags=["Evidence"])


def next_evidence_id(project_id: str, db: Session) -> str:
    # Evidence.id is the global primary key, so a project-local EVID-001
    # sequence can collide with legacy or another project's record. A short
    # stable identifier keeps the human-friendly EVID- prefix without that
    # collision risk.
    while True:
        candidate = f"EVID-{uuid.uuid4().hex[:10].upper()}"
        if not db.query(Evidence.id).filter(Evidence.id == candidate).first():
            return candidate


def evidence_metadata(evidence: Evidence) -> dict:
    return {
        "evidence_id": evidence.id,
        "task_id": evidence.task_id,
        "task_title": evidence.task.title if evidence.task else None,
        "step_id": evidence.step_id,
        "step_title": evidence.step.title if evidence.step else None,
        "created_at": evidence.created_at,
        "file_path": evidence.file_path,
        "file_size_bytes": evidence.file_size_bytes,
        "sha256_hash": evidence.sha256_hash,
        "redacted_excerpt": evidence.redacted_excerpt,
    }


def verify_and_persist_evidence(
    project_id: str,
    task: Task,
    raw: str,
    db: Session,
    step: TaskStep | None = None,
) -> dict:
    evidence_id = next_evidence_id(project_id, db)
    relative_path, size, digest, _filename = save_artifact(project_id, evidence_id, raw)
    evidence = Evidence(
        id=evidence_id,
        project_id=project_id,
        task_id=task.id,
        step_id=step.id if step else None,
        evidence_type="TERMINAL_LOG",
        file_path=relative_path,
        file_size_bytes=size,
        sha256_hash=digest,
        redacted_excerpt=create_safe_excerpt(raw),
    )
    db.add(evidence)

    subject = step or task
    verdict = verify_task_evidence(subject.title, subject.objective, raw)
    if verdict.verdict == "PASS":
        subject.status = "COMPLETED"
    elif verdict.verdict == "CONFIRMED_NEGATIVE":
        subject.status = "CONFIRMED_NEGATIVE"
        subject.justification = verdict.summary

    for asset in verdict.extracted_assets:
        if not db.query(Asset).filter(
            Asset.project_id == project_id, Asset.value == asset.value
        ).first():
            db.add(Asset(
                id=str(uuid.uuid4()),
                project_id=project_id,
                type=asset.type,
                value=asset.value,
                source_task_id=task.id,
            ))
        if any(word in asset.value.lower() for word in [
            "backup", "admin", "zip", ".env", "config", "graphql"
        ]):
            duplicate = db.query(WorkflowProposal).filter(
                WorkflowProposal.project_id == project_id,
                WorkflowProposal.target_asset == asset.value,
            ).first()
            if not duplicate:
                refined = suggest_safe_tasks(asset.type, asset.value, workflow_context(db, project_id))[:1]
                proposal = refined[0] if refined else None
                db.add(WorkflowProposal(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    phase_name=proposal.phase_name if proposal else DEFAULT_PHASE,
                    title=f"Investigate Exposed Asset: {asset.value}",
                    objective=proposal.objective if proposal else f"Evaluate whether exposed asset {asset.value} leaks sensitive information or permits unauthorized access.",
                    priority="HIGH",
                    target_asset=asset.value,
                    action_type="INVESTIGATION",
                ))

    rollup_task_from_steps(task, project_id, db)
    details = {"task_id": task.id, "verdict": verdict.verdict}
    if step:
        details["step_id"] = step.id
    record_event(db, project_id, "EVIDENCE_VERIFIED", "evidence", evidence.id, details)
    response = {
        "verdict": verdict.verdict,
        "confidence": verdict.confidence,
        "summary": verdict.summary,
        "grounded_quotations": verdict.grounded_quotations,
        "extracted_assets": [asset.model_dump() for asset in verdict.extracted_assets],
        "evidence_id": evidence.id,
        "task_status": task.status,
    }
    if step:
        response["step_status"] = step.status
    db.commit()
    return response


@router.post("/api/v1/projects/{project_id}/tasks/{task_id}/verify")
def verify_evidence(
    project_id: str,
    task_id: str,
    payload: EvidenceSubmit,
    db: Session = Depends(get_db),
):
    scope = db.query(Scope).filter(Scope.project_id == project_id).first()
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not scope or not scope.is_locked:
        raise HTTPException(400, "Cannot verify evidence while scope is unlocked")
    if not task:
        raise HTTPException(404, "Task not found")
    if active_steps(task, db):
        raise HTTPException(409, "this task uses step-level verification")

    raw = payload.raw_content.strip()
    return verify_and_persist_evidence(project_id, task, raw, db)


@router.get("/api/v1/projects/{project_id}/evidence")
def list_evidence(project_id: str, db: Session = Depends(get_db)):
    records = db.query(Evidence).filter(
        Evidence.project_id == project_id
    ).order_by(Evidence.created_at.desc()).all()
    return [evidence_metadata(record) for record in records]


@router.get("/api/v1/projects/{project_id}/evidence/{evidence_id}/content")
def get_evidence_content(project_id: str, evidence_id: str, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.project_id == project_id,
    ).first()
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    if not evidence.file_path:
        if evidence.raw_content is None:
            raise HTTPException(404, "Artifact file not found")
        return {"content": evidence.raw_content}
    try:
        content = read_artifact(project_id, Path(evidence.file_path).name)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(404, str(error)) from error
    return {"content": content}
