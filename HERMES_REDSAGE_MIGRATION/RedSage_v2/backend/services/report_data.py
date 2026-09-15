"""Shared loaders for markdown report inputs (preview, download, archive snapshot)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.schema import Asset, Evidence, Finding, Project, Scope, ScopeAmendment, Task


def load_report_context(db: Session, project_id: str):
    """Return project + related rows used by ``build_markdown_report``.

    Tasks are limited to non-archived rows so report preview/download and the
    archive ``reports/report.md`` snapshot stay consistent.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    scope = db.query(Scope).filter(Scope.project_id == project_id).first()
    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.is_archived.is_(False))
        .order_by(Task.order_index)
        .all()
    )
    findings = db.query(Finding).filter(Finding.project_id == project_id).all()
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    evidence = (
        db.query(Evidence)
        .filter(Evidence.project_id == project_id)
        .order_by(Evidence.created_at)
        .all()
    )
    amendments = (
        db.query(ScopeAmendment)
        .filter(ScopeAmendment.project_id == project_id)
        .order_by(ScopeAmendment.created_at)
        .all()
    )
    return project, scope, tasks, findings, assets, evidence, amendments
