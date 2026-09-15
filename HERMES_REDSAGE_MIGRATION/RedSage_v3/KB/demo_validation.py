"""Validate the internal workflow-generator demonstration artifact."""
from __future__ import annotations
from pathlib import Path

REQUIRED_SECTIONS = (
    "## Source problem statement",
    "## Workflow generator result",
    "### 2. Authorization and safety gate",
    "### 4. Initial roadmap",
    "### 5. Stop conditions",
    "### 6. Human approval gates",
)


def validate_demo_document(path: str | Path) -> dict[str, object]:
    text = Path(path).read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    lowered = text.lower()
    if "not authorization to test any real target" not in lowered:
        missing.append("real-target authorization disclaimer")
    return {"passed": not missing, "missing": missing}
