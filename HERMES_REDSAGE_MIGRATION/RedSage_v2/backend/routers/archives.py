from __future__ import annotations

import io
import json
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.schema import (
    Asset, AuditEvent, Evidence, Finding, Phase, Project, Scope,
    ScopeAmendment, Task, TaskStep, MentorMessage, WorkflowProposal,
)
from backend.services.archive_service import (
    ARCHIVE_FORMAT_VERSION, artifact_member_path, checksum, json_bytes,
    utc_now_iso, validate_archive, validate_zip_member,
)
from backend.services.artifact_manager import ensure_project_artifacts_dir, safe_join
from backend.services.report_builder import build_markdown_report
from backend.services.report_data import load_report_context

router = APIRouter(prefix="/api/v1/projects", tags=["Project Archives"])


def iso(value):
    return value.isoformat() if value else None


def row(model, columns):
    return {column: iso(getattr(model, column)) if column.endswith("_at") else getattr(model, column) for column in columns}


def project_data(project_id: str, db: Session):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    scope = db.query(Scope).filter(Scope.project_id == project_id).first()
    amendments = db.query(ScopeAmendment).filter(ScopeAmendment.project_id == project_id).all()
    phases = db.query(Phase).filter(Phase.project_id == project_id).all()
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    evidence = db.query(Evidence).filter(Evidence.project_id == project_id).all()
    findings = db.query(Finding).filter(Finding.project_id == project_id).all()
    proposals = db.query(WorkflowProposal).filter(WorkflowProposal.project_id == project_id).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.project_id == project_id).all()
    steps = db.query(TaskStep).join(Task, TaskStep.task_id == Task.id).filter(Task.project_id == project_id).all()
    mentor_messages = db.query(MentorMessage).filter(MentorMessage.project_id == project_id).all()
    return project, scope, amendments, phases, tasks, steps, assets, evidence, findings, proposals, audit_events, mentor_messages


@router.get("/{project_id}/export")
def export_project(project_id: str, db: Session = Depends(get_db)):
    project, scope, amendments, phases, tasks, steps, assets, evidence, findings, proposals, audit_events, mentor_messages = project_data(project_id, db)
    members: dict[str, bytes] = {}
    data = {
        "projects": [row(project, ["id", "name", "description", "brief", "target_type", "status", "created_at"])],
        "scopes": [row(scope, ["id", "project_id", "in_scope_whitelist", "out_of_scope_blacklist", "max_rate_limit", "is_locked", "locked_at"])] if scope else [],
        "scope_amendments": [row(item, ["id", "project_id", "added_targets", "authorized_by", "rationale", "created_at"]) for item in amendments],
        "phases": [row(item, ["id", "project_id", "name", "order_index", "is_archived", "archived_at", "archived_by"]) for item in phases],
        "tasks": [row(item, ["id", "phase_id", "project_id", "title", "objective", "command_template", "status", "priority", "order_index", "is_ai_proposed", "justification", "is_archived", "archived_at", "archived_by"]) for item in tasks],
        "task_steps": [row(item, ["id", "task_id", "title", "objective", "why_it_matters", "completion_criteria", "expected_evidence_type", "status", "order_index", "is_ai_proposed", "is_archived", "archived_at", "archived_by", "justification"]) for item in steps],
        "workflow_proposals": [row(item, ["id", "project_id", "phase_name", "title", "objective", "priority", "target_asset", "action_type", "status", "created_task_id", "created_at"]) for item in proposals],
        "assets": [row(item, ["id", "project_id", "type", "value", "source_task_id"]) for item in assets],
        "evidence": [row(item, ["id", "project_id", "task_id", "step_id", "evidence_type", "file_path", "file_size_bytes", "sha256_hash", "redacted_excerpt", "created_at"]) for item in evidence],
        "findings": [row(item, ["id", "project_id", "title", "severity", "status", "affected_asset", "description", "reproduction_steps", "remediation", "evidence_id"]) for item in findings],
        "audit_events": [row(item, ["id", "project_id", "event_type", "entity_type", "entity_id", "details", "created_at"]) for item in audit_events],
        "mentor_messages": [row(item, ["id", "project_id", "task_id", "step_id", "mode", "role", "content", "ai_available", "created_at"]) for item in mentor_messages],
    }
    data_bytes = json_bytes(data)
    members["db/project_data.json"] = data_bytes
    for item in evidence:
        member = artifact_member_path(item.file_path, item.id)
        source = Path(item.file_path) if item.file_path else None
        source = source if source and source.is_absolute() else (Path(__file__).resolve().parents[2] / source if source else None)
        if source and source.is_file():
            members[member] = source.read_bytes()
        elif item.raw_content is not None:
            members[member] = item.raw_content.encode("utf-8")
        else:
            raise HTTPException(409, f"Evidence artifact is missing: {item.id}")
    # Prefer the shared loader so archive report.md matches /report preview.
    context = load_report_context(db, project_id)
    if context:
        _project, _scope, report_tasks, report_findings, report_assets, report_evidence, report_amendments = context
        report = build_markdown_report(_project, _scope, report_tasks, report_findings, report_assets, report_evidence, report_amendments)
    else:
        report = build_markdown_report(project, scope, [item for item in tasks if not item.is_archived], findings, assets, evidence, amendments)
    members["reports/report.md"] = report.encode("utf-8")
    manifest = {
        "format_version": ARCHIVE_FORMAT_VERSION,
        "exported_at_utc": utc_now_iso(),
        "project_id": project_id,
        "counts": {name: len(items) for name, items in data.items()},
        "checksums": [{"path": path, "sha256": checksum(content), "size_bytes": len(content)} for path, content in members.items()],
    }
    members["manifest.json"] = json_bytes(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in {"manifest.json": members.pop("manifest.json"), **members}.items():
            archive.writestr(path, content)
    filename = f"redsage_project_{project_id}_{datetime.now(timezone.utc):%Y%m%d}.zip"
    return Response(buffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def require_dict(data, key):
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"Archive field {key} must be a list")
    return value


def remap_entity_id(entity_type, entity_id, id_maps):
    if not entity_id:
        return None
    mapping = {
        "scope": "scope",
        "scope_amendment": "amendment",
        "task": "task",
        "asset": "asset",
        "evidence": "evidence",
        "finding": "finding",
        "proposal": "proposal",
    }.get(entity_type)
    return id_maps.get(mapping, {}).get(entity_id, entity_id) if mapping else entity_id


@router.post("/import")
async def import_project(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload a .zip project archive")
    archive_bytes = await file.read()
    try:
        archive, manifest = validate_archive(archive_bytes)
    except (ValueError, zipfile.BadZipFile) as error:
        raise HTTPException(400, str(error)) from error
    try:
        data = json.loads(archive.read("db/project_data.json"))
        if not isinstance(data, dict) or len(require_dict(data, "projects")) != 1:
            raise ValueError("Archive must contain exactly one project")
        checksums = {item["path"]: item["sha256"] for item in manifest.get("checksums", [])}
        required_members = {"db/project_data.json"}
        required_members.update(artifact_member_path(item.get("file_path"), item["id"]) for item in require_dict(data, "evidence"))
        archive_names = {info.filename for info in archive.infolist()}
        if not required_members.issubset(archive_names):
            raise ValueError("Archive is missing project data or evidence artifacts")
        if not required_members.issubset(checksums):
            raise ValueError("Manifest is missing required checksums")
        for info in archive.infolist():
            path = validate_zip_member(info.filename)
            if path != "manifest.json" and path in checksums and checksum(archive.read(info.filename)) != checksums[path]:
                raise ValueError(f"Checksum mismatch for archive member: {path}")
        source_project = data["projects"][0]
        new_project_id = str(uuid.uuid4())
        id_maps = {"project": {source_project["id"]: new_project_id}, "scope": {}, "amendment": {}, "phase": {}, "task": {}, "step": {}, "asset": {}, "evidence": {}, "finding": {}, "proposal": {}, "audit": {}, "mentor": {}}
        project_dir = ensure_project_artifacts_dir(new_project_id)
        artifact_paths = {}
        try:
            for source_evidence in require_dict(data, "evidence"):
                old_id = source_evidence["id"]
                new_id = f"EVID-{uuid.uuid4().hex[:10].upper()}"
                id_maps["evidence"][old_id] = new_id
                member = artifact_member_path(source_evidence.get("file_path"), old_id)
                artifact_name = f"{new_id}_{uuid.uuid4().hex[:10]}.txt"
                target = safe_join(project_dir, artifact_name)
                target.write_bytes(archive.read(member))
                artifact_paths[old_id] = target.relative_to(Path(__file__).resolve().parents[2]).as_posix()
            id_maps["scope"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "scopes")}
            id_maps["amendment"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "scope_amendments")}
            id_maps["phase"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "phases")}
            id_maps["task"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "tasks")}
            id_maps["step"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "task_steps")}
            id_maps["asset"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "assets")}
            id_maps["finding"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "findings")}
            id_maps["proposal"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "workflow_proposals")}
            id_maps["audit"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "audit_events")}
            id_maps["mentor"] = {item["id"]: str(uuid.uuid4()) for item in require_dict(data, "mentor_messages")}
            project = Project(id=new_project_id, name=source_project["name"], description=source_project.get("description"), brief=source_project.get("brief"), target_type=source_project.get("target_type", "web_app"), status=source_project.get("status", "IN_PROGRESS"), created_at=parse_datetime(source_project.get("created_at")))
            db.add(project)
            for item in require_dict(data, "scopes"):
                db.add(Scope(id=id_maps["scope"][item["id"]], project_id=new_project_id, in_scope_whitelist=item["in_scope_whitelist"], out_of_scope_blacklist=item["out_of_scope_blacklist"], max_rate_limit=item.get("max_rate_limit", 10), is_locked=item.get("is_locked", False), locked_at=parse_datetime(item.get("locked_at"))))
            for item in require_dict(data, "scope_amendments"):
                db.add(ScopeAmendment(id=id_maps["amendment"][item["id"]], project_id=new_project_id, added_targets=item["added_targets"], authorized_by=item["authorized_by"], rationale=item["rationale"], created_at=parse_datetime(item.get("created_at"))))
            for item in require_dict(data, "phases"):
                db.add(Phase(id=id_maps["phase"][item["id"]], project_id=new_project_id, name=item["name"], order_index=item["order_index"], is_archived=item.get("is_archived", False), archived_at=parse_datetime(item.get("archived_at")), archived_by=item.get("archived_by")))
            for item in require_dict(data, "tasks"):
                db.add(Task(id=id_maps["task"][item["id"]], phase_id=id_maps["phase"][item["phase_id"]], project_id=new_project_id, title=item["title"], objective=item["objective"], command_template=item.get("command_template"), status=item.get("status", "NOT_STARTED"), priority=item.get("priority", "MEDIUM"), order_index=item["order_index"], is_ai_proposed=item.get("is_ai_proposed", False), justification=item.get("justification"), is_archived=item.get("is_archived", False), archived_at=parse_datetime(item.get("archived_at")), archived_by=item.get("archived_by")))
            for item in require_dict(data, "task_steps"):
                db.add(TaskStep(id=id_maps["step"][item["id"]], task_id=id_maps["task"][item["task_id"]], title=item["title"], objective=item.get("objective", ""), why_it_matters=item.get("why_it_matters", ""), completion_criteria=item.get("completion_criteria", ""), expected_evidence_type=item.get("expected_evidence_type", "TERMINAL_LOG"), status=item.get("status", "NOT_STARTED"), order_index=item.get("order_index", 1), is_ai_proposed=item.get("is_ai_proposed", False), is_archived=item.get("is_archived", False), archived_at=parse_datetime(item.get("archived_at")), archived_by=item.get("archived_by"), justification=item.get("justification")))
            for old_id, file_path in artifact_paths.items():
                item = next(item for item in data["evidence"] if item["id"] == old_id)
                content = (Path(__file__).resolve().parents[2] / file_path).read_bytes()
                db.add(Evidence(id=id_maps["evidence"][old_id], project_id=new_project_id, task_id=id_maps["task"][item["task_id"]], step_id=id_maps["step"].get(item.get("step_id")), evidence_type=item.get("evidence_type", "TERMINAL_LOG"), file_path=file_path, file_size_bytes=len(content), sha256_hash=checksum(content), redacted_excerpt=item.get("redacted_excerpt", ""), created_at=parse_datetime(item.get("created_at"))))
            for item in require_dict(data, "assets"):
                db.add(Asset(id=id_maps["asset"][item["id"]], project_id=new_project_id, type=item["type"], value=item["value"], source_task_id=id_maps["task"].get(item.get("source_task_id"))))
            for item in require_dict(data, "findings"):
                db.add(Finding(id=id_maps["finding"][item["id"]], project_id=new_project_id, title=item["title"], severity=item["severity"], status=item.get("status", "DRAFT"), affected_asset=item.get("affected_asset"), description=item["description"], reproduction_steps=item["reproduction_steps"], remediation=item.get("remediation"), evidence_id=id_maps["evidence"].get(item.get("evidence_id"))))
            for item in require_dict(data, "workflow_proposals"):
                db.add(WorkflowProposal(id=id_maps["proposal"][item["id"]], project_id=new_project_id, phase_name=item["phase_name"], title=item["title"], objective=item["objective"], priority=item.get("priority", "MEDIUM"), target_asset=item["target_asset"], action_type=item["action_type"], status=item.get("status", "PENDING"), created_task_id=id_maps["task"].get(item.get("created_task_id")), created_at=parse_datetime(item.get("created_at"))))
            for item in require_dict(data, "mentor_messages"):
                db.add(MentorMessage(id=id_maps["mentor"][item["id"]], project_id=new_project_id, task_id=id_maps["task"].get(item.get("task_id")), step_id=id_maps["step"].get(item.get("step_id")), mode=item.get("mode", "teach"), role=item.get("role", "assistant"), content=item.get("content", ""), ai_available=item.get("ai_available"), created_at=parse_datetime(item.get("created_at"))))
            for item in require_dict(data, "audit_events"):
                details = json.loads(item.get("details", "{}")) if isinstance(item.get("details", "{}"), str) else item.get("details", {})
                for key, mapping in (("task_id", "task"), ("evidence_id", "evidence"), ("proposal_id", "proposal")):
                    if details.get(key) in id_maps[mapping]:
                        details[key] = id_maps[mapping][details[key]]
                db.add(AuditEvent(id=id_maps["audit"][item["id"]], project_id=new_project_id, event_type=item["event_type"], entity_type=item.get("entity_type"), entity_id=remap_entity_id(item.get("entity_type"), item.get("entity_id"), id_maps), details=json.dumps(details), created_at=parse_datetime(item.get("created_at"))))
            db.commit()
        except Exception:
            db.rollback()
            shutil.rmtree(project_dir.parent, ignore_errors=True)
            raise
    except (KeyError, ValueError, zipfile.BadZipFile) as error:
        raise HTTPException(400, f"Invalid project archive: {error}") from error
    finally:
        archive.close()
    return {"status": "imported", "project_id": new_project_id}
