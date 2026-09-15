"""Refresh Chroma metadata from an enriched manifest without Cohere calls."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

_FIELDS = (
    "source_id", "path", "ordinal", "content_hash", "source_version_id",
    "document_id", "title", "locator", "source_type", "content_class",
    "environment_scope", "is_approved", "is_unsafe", "trust_level",
    "policy_tags", "metadata_schema_version",
)

def refresh_collection_metadata(
    manifest_path: str | Path,
    *,
    client: Any | None = None,
    collection_name: str = "redsage_v3_workflow_cohere_v1",
    batch_size: int = 256,
) -> dict[str, Any]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("manifest_type") != "redsage_v3_workflow_kb_preview":
        raise ValueError("unsupported workflow KB manifest")
    chunks = manifest.get("chunks", [])
    if client is None:
        import chromadb
        client = chromadb.PersistentClient(path="data/kb_build/chroma")
    collection = client.get_collection(collection_name)
    updated = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.update(
            ids=[str(chunk["chunk_id"]) for chunk in batch],
            metadatas=[{field: chunk.get(field, "") for field in _FIELDS} for chunk in batch],
        )
        updated += len(batch)
    return {"collection_name": collection_name, "updated_count": updated, "cohere_calls": 0}

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = refresh_collection_metadata(root / "data" / "kb_build" / "workflow_preview_manifest.json")
    print(json.dumps(result, indent=2))
