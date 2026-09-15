"""Select and classify identity/session sources for the next KB domain."""
from __future__ import annotations
from pathlib import Path
from KB.workflow_sources import is_selectable_workflow_source

_IDENTITY_TERMS = (
    "authentication", "session", "oauth", "jwt", "cookie", "login",
    "identity", "password", "multifactor", "mfa", "saml", "account",
)
_EXCLUDE_TERMS = ("authorization", "access_control", "idor", "insecure_direct_object")


def select_identity_sources(root: str | Path) -> list[Path]:
    root = Path(root)
    selected: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_selectable_workflow_source(path):
            continue
        relative = path.relative_to(root).as_posix()
        lower = relative.lower()
        if not lower.startswith(("03_owasp/", "04_cwe_cvss/", "05_web_platform_docs/", "02_redsage_domain/")):
            continue
        if any(term in lower for term in _EXCLUDE_TERMS):
            continue
        if any(term in lower for term in _IDENTITY_TERMS):
            selected.append(path)
    return sorted(selected)
