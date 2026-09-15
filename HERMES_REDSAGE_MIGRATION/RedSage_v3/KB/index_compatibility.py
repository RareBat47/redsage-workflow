"""Fail-closed compatibility checks for versioned KB indexes."""
from __future__ import annotations
from pathlib import Path
from typing import Any


def validate_manifest_identity(manifest: dict[str, Any], collection_name: str) -> None:
    declared = manifest.get("collection_name")
    if not declared:
        raise ValueError("manifest collection_name is required")
    if declared != collection_name:
        raise ValueError(f"collection name mismatch: manifest={declared!r}, requested={collection_name!r}")


def validate_collection_metadata(metadata: dict[str, Any], *, model: str, schema_version: str, policy_version: str, manifest_path: str, manifest_sha256: str | None = None) -> None:
    expected = {"model": model, "metadata_schema_version": schema_version, "policy_version": policy_version, "source_manifest": str(manifest_path)}
    if manifest_sha256 is not None:
        expected["source_manifest_sha256"] = manifest_sha256
    for key, value in expected.items():
        if key not in metadata:
            raise ValueError(f"{key} missing from existing collection metadata")
        actual = metadata[key]
        if str(actual) != str(value):
            raise ValueError(f"{key} mismatch: existing={actual!r}, expected={value!r}")


def manifest_chunk_ids(manifest: dict[str, Any]) -> set[str]:
    return {str(item["chunk_id"]) for item in manifest.get("chunks", [])}


def collection_ids(collection: Any, *, batch_size: int = 1000) -> set[str]:
    count = collection.count()
    ids: set[str] = set()
    for offset in range(0, count, batch_size):
        result = collection.get(include=[], limit=batch_size, offset=offset)
        ids.update(str(item) for item in result.get("ids", []))
    return ids


def reconcile_collection_ids(manifest_ids: set[str], collection: Any, *, delete_stale: bool = False) -> dict[str, list[str]]:
    current_ids = collection_ids(collection)
    stale_ids = sorted(current_ids - set(manifest_ids))
    missing_ids = sorted(set(manifest_ids) - current_ids)
    deleted_ids: list[str] = []
    if delete_stale and stale_ids:
        collection.delete(ids=stale_ids)
        deleted_ids = stale_ids
    return {"stale_ids": stale_ids, "missing_ids": missing_ids, "deleted_ids": deleted_ids}


def validate_collection_ids(manifest: dict[str, Any], collection: Any) -> dict[str, list[str]]:
    result = reconcile_collection_ids(manifest_chunk_ids(manifest), collection)
    if result["stale_ids"]:
        raise ValueError(f"stale collection IDs present: {result['stale_ids'][:3]}")
    return result
