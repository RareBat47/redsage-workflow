"""Server-side safety and visibility decisions for KB retrieval."""
from __future__ import annotations
from typing import Any

ALLOWED_ENGAGEMENT_SCOPES = frozenset({"authorized_engagement", "shared_reference", "all"})


def policy_decision(chunk: dict[str, Any], *, environment_scope: str, tenant_id: str | None = None, include_lab: bool = False) -> tuple[bool, str]:
    if not chunk.get("is_approved", False):
        return False, "not_approved"
    if chunk.get("is_unsafe", True):
        return False, "unsafe"
    if "environment_scope" not in chunk:
        return False, "unknown_scope"
    scope = str(chunk.get("environment_scope", "unknown"))
    if environment_scope == "lab_only":
        if scope != "lab_only": return False, "not_lab_scope"
    elif scope == "lab_only" and not include_lab:
        return False, "lab_excluded"
    elif scope not in ALLOWED_ENGAGEMENT_SCOPES:
        return False, "unknown_scope"
    chunk_tenant = chunk.get("tenant_id")
    if chunk_tenant is not None and chunk_tenant != tenant_id:
        return False, "tenant_mismatch"
    return True, "allowed"


def filter_chunks(chunks: list[dict[str, Any]], *, environment_scope: str = "authorized_engagement", tenant_id: str | None = None, include_lab: bool = False) -> list[dict[str, Any]]:
    return [chunk for chunk in chunks if policy_decision(chunk, environment_scope=environment_scope, tenant_id=tenant_id, include_lab=include_lab)[0]]


def filter_chunks_with_reasons(chunks: list[dict[str, Any]], *, environment_scope: str = "authorized_engagement", tenant_id: str | None = None, include_lab: bool = False) -> tuple[list[dict[str, Any]], list[str]]:
    allowed, reasons = [], []
    for chunk in chunks:
        permitted, reason = policy_decision(chunk, environment_scope=environment_scope, tenant_id=tenant_id, include_lab=include_lab)
        if permitted: allowed.append(chunk)
        else: reasons.append(reason)
    return allowed, reasons
