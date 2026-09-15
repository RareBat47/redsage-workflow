"""Filesystem-backed, plain-text evidence artifact storage."""

from __future__ import annotations

import hashlib
import os
import re
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = PROJECT_ROOT / "data" / "projects"
MAX_ARTIFACT_BYTES = 10 * 1024 * 1024


def artifact_too_large_error() -> ValueError:
    megabytes = MAX_ARTIFACT_BYTES // (1024 * 1024)
    return ValueError(f"Artifact exceeds the {megabytes} MB size limit")


def ensure_project_artifacts_dir(project_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", project_id):
        raise ValueError("Invalid project identifier")
    path = (ARTIFACTS_ROOT / project_id / "artifacts").resolve()
    root = ARTIFACTS_ROOT.resolve()
    if root not in path.parents:
        raise ValueError("Invalid project artifact directory")
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_join(base_dir: str | Path, filename: str) -> Path:
    base = Path(base_dir).resolve()
    candidate = (base / filename).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("Invalid artifact path: Directory traversal detected")
    return candidate


def save_artifact(project_id: str, evidence_id: str, raw_text: str) -> tuple[str, int, str, str]:
    if not isinstance(raw_text, str):
        raise TypeError("Artifact content must be plain text")
    raw_bytes = raw_text.encode("utf-8")
    if len(raw_bytes) > MAX_ARTIFACT_BYTES:
        raise artifact_too_large_error()
    filename = f"{evidence_id}_{int(time.time())}.txt"
    directory = ensure_project_artifacts_dir(project_id)
    target = safe_join(directory, filename)
    temporary = target.with_name(f".{target.name}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(raw_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        try:
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        if temporary.exists():
            temporary.unlink()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    try:
        relative_path = target.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        # Keep tests and alternate storage roots portable while retaining the
        # repository-relative path used by the production database.
        relative_path = target.relative_to(ARTIFACTS_ROOT.parent.parent).as_posix()
    return relative_path, len(raw_bytes), digest, filename


def read_artifact(project_id: str, filename: str) -> str:
    directory = ensure_project_artifacts_dir(project_id)
    target = safe_join(directory, filename)
    if target.suffix.lower() not in {".txt", ".log"}:
        raise ValueError("Only plain-text artifacts can be read")
    if not target.is_file():
        raise FileNotFoundError("Artifact not found")
    if target.stat().st_size > MAX_ARTIFACT_BYTES:
        raise artifact_too_large_error()
    return target.read_text(encoding="utf-8")
