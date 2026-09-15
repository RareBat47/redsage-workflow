"""Append-only retrieval receipts without storing raw queries by default."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import uuid
from typing import Any


def write_retrieval_receipt(
    directory: str | Path,
    *,
    actor_type: str,
    index_profile: str,
    policy_version: str,
    selected_chunk_ids: list[str],
    score_components: dict[str, dict[str, float]] | None = None,
    query: str | None = None,
    project_id: str | None = None,
    warnings: list[str] | None = None,
    query_classification: str | None = None,
    ranking_profile: str | None = None,
    environment_scope: str | None = None,
    candidate_count: int | None = None,
    filtered_count: int | None = None,
    filtered_reasons: dict[str, int] | None = None,
) -> dict[str, Any]:
    if not actor_type.strip():
        raise ValueError("actor_type is required")
    query_hash = hashlib.sha256((query or "").encode("utf-8")).hexdigest()
    receipt = {
        "receipt_type": "redsage_v3_workflow_retrieval",
        "query_id": f"qry_{uuid.uuid4().hex}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "actor_type": actor_type,
        "project_id": project_id,
        "query_hash": query_hash,
        "policy_version": policy_version,
        "index_profile": index_profile,
        "selected_chunk_ids": list(selected_chunk_ids),
        "score_components": score_components or {},
        "warnings": warnings or [],
        "query_classification": query_classification,
        "ranking_profile": ranking_profile,
        "environment_scope": environment_scope,
        "candidate_count": candidate_count,
        "filtered_count": filtered_count,
        "filtered_reasons": filtered_reasons or {},
    }
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{receipt['query_id']}.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    return receipt
