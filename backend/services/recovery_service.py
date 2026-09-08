"""Startup reconciliation for filesystem-backed evidence artifacts."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.schema import Evidence

logger = logging.getLogger("redsage.recovery")


def reconcile_storage_and_db(db: Session, data_dir: str | Path = "data/projects") -> dict[str, int]:
    root = Path(data_dir)
    cleaned = 0
    temporary_files = root.glob("**/artifacts/.*.tmp") if root.exists() else []
    for temporary in temporary_files:
        try:
            temporary.unlink()
            cleaned += 1
        except OSError:
            logger.exception("Failed to remove stale artifact temporary file")

    missing = 0
    if db is not None:
        for record in db.query(Evidence).all():
            if record.file_path and not Path(record.file_path).is_file():
                missing += 1
                logger.critical("Evidence %s references missing artifact", record.id)

    return {"cleaned_tmp_files": cleaned, "missing_records": missing}
