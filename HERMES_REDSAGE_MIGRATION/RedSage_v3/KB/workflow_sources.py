"""Select safe documentation inputs for workflow-generation KB ingestion."""

from __future__ import annotations

from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".rst", ".html", ".json"}
EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".github",
    "assets",
    "images",
    "fonts",
    "_archives",
}
EXCLUDED_SUFFIXES = {
    ".zip",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ttf",
    ".woff",
    ".woff2",
    ".lock",
}


def is_selectable_workflow_source(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_PARTS:
        return False
    suffix = path.suffix.lower()
    if suffix in EXCLUDED_SUFFIXES:
        return False
    if suffix not in TEXT_SUFFIXES:
        return False
    if path.name.lower() in {"package.json", "package-lock.json", "requirements.txt"}:
        return False
    return True


def select_workflow_sources(root: str | Path) -> list[Path]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted(
        path for path in root.rglob("*") if path.is_file() and is_selectable_workflow_source(path)
    )
