"""Project-scoped JSON archive creation and safe ZIP member validation."""

from __future__ import annotations

import hashlib
import io
import json
import posixpath
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from backend.services.artifact_manager import PROJECT_ROOT, read_artifact

ARCHIVE_FORMAT_VERSION = "1.0"
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_MEMBER_BYTES = 10 * 1024 * 1024


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_zip_member(name: str) -> str:
    """Return a normalized safe member name or raise ValueError."""
    if not name or "\\" in name or name.startswith("/") or name.startswith("\\"):
        raise ValueError("Archive contains an unsafe absolute path")
    normalized = posixpath.normpath(name)
    if normalized in {".", ""} or normalized.startswith("../") or normalized == ".." or "/../" in f"/{normalized}":
        raise ValueError("Archive contains a directory traversal path")
    if any(part in {"", "."} for part in normalized.split("/")):
        raise ValueError("Archive contains an invalid path")
    return normalized


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True, default=str).encode("utf-8")


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_archive(data: bytes) -> tuple[zipfile.ZipFile, dict]:
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError("Archive exceeds the 100 MB size limit")
    archive = zipfile.ZipFile(io.BytesIO(data))
    if len(archive.infolist()) > 1000:
        archive.close()
        raise ValueError("Archive contains too many members")
    total_size = 0
    for info in archive.infolist():
        validate_zip_member(info.filename)
        if info.file_size > MAX_MEMBER_BYTES:
            archive.close()
            raise ValueError("Archive member exceeds the 10 MB size limit")
        total_size += info.file_size
        if total_size > MAX_ARCHIVE_BYTES:
            archive.close()
            raise ValueError("Archive expands beyond the 100 MB size limit")
    try:
        manifest = json.loads(archive.read("manifest.json"))
    except (KeyError, json.JSONDecodeError) as error:
        archive.close()
        raise ValueError("Archive must contain a valid manifest.json") from error
    if manifest.get("format_version") != ARCHIVE_FORMAT_VERSION:
        archive.close()
        raise ValueError("Unsupported archive format version")
    return archive, manifest


def artifact_member_path(file_path: str | None, evidence_id: str) -> str:
    filename = Path(file_path).name if file_path else f"{evidence_id}.txt"
    validate_zip_member(filename)
    if Path(filename).suffix.lower() not in {".txt", ".log"}:
        raise ValueError("Only plain-text artifact files can be archived")
    return f"artifacts/{filename}"
