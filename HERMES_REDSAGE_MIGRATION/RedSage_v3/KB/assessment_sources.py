"""Select Web Application assessment guidance sources for KB-02."""
from __future__ import annotations
from pathlib import Path
from KB.workflow_sources import is_selectable_workflow_source


def select_assessment_sources(root: str | Path) -> list[Path]:
    root = Path(root)
    selected = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_selectable_workflow_source(path):
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith("08_lab_ctf/") or relative.startswith("01_methodology_book/"):
            continue
        if relative.startswith(("03_owasp/", "04_cwe_cvss/", "05_web_platform_docs/", "09_scope_authorization/", "10_stop_escalation/", "02_redsage_domain/")):
            selected.append(path)
    return sorted(selected)
