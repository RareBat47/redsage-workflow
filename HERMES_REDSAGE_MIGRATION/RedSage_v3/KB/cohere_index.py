"""Build an isolated ChromaDB index from an approved workflow manifest."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from KB.cohere_embeddings import CohereEmbeddingAdapter


def _load_manifest(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("manifest_type") not in {
        "redsage_v3_workflow_kb_preview",
        "redsage_v3_assessment_kb_preview",
        "redsage_v3_reporting_kb_preview",
        "redsage_v3_identity_kb_preview",
        "redsage_v3_authorization_kb_preview",
        "redsage_v3_api_kb_preview",
    }:
        raise ValueError("unsupported workflow KB manifest")
    return data


def _batch(items: list[dict[str, Any]], size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def build_cohere_index(
    manifest_path: str | Path,
    *,
    client: Any | None = None,
    embedder: Any | None = None,
    collection_name: str = "redsage_v3_workflow_cohere_v1",
    batch_size: int = 96,
    receipt_path: str | Path | None = None,
    progress_path: str | Path | None = None,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Embed manifest chunks with Cohere and upsert them into ChromaDB.

    The caller supplies a client in tests; production lazily creates a local
    PersistentClient. Existing collections are never deleted.
    """
    manifest = _load_manifest(manifest_path)
    from KB.index_compatibility import validate_manifest_identity
    validate_manifest_identity(manifest, collection_name)
    chunks = manifest.get("chunks", [])
    manifest_sha256 = hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest()
    if not isinstance(chunks, list):
        raise ValueError("manifest chunks must be a list")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    if embedder is None:
        embedder = CohereEmbeddingAdapter()
    if client is None:
        import chromadb

        client = chromadb.PersistentClient(path="data/kb_build/chroma")
    manifest_profile = manifest.get("manifest_type", "")
    schema_version = "workflow-metadata-v1"
    policy_version = "workflow-v1"
    if manifest_profile == "redsage_v3_assessment_kb_preview": schema_version = policy_version = "assessment-v1"
    elif manifest_profile == "redsage_v3_reporting_kb_preview": schema_version = policy_version = "reporting-v1"
    elif manifest_profile == "redsage_v3_identity_kb_preview": schema_version = policy_version = "identity-v1"
    elif manifest_profile == "redsage_v3_authorization_kb_preview": schema_version = policy_version = "authorization-v1"
    elif manifest_profile == "redsage_v3_api_kb_preview": schema_version = policy_version = "api-v1"
    model = embedder.model if hasattr(embedder, "model") else "unknown"
    index_profile = json.dumps(getattr(embedder, "index_profile", {}), sort_keys=True)
    metadata = {
        "provider": "cohere",
        "model": model,
        "index_profile": index_profile,
        "metadata_schema_version": schema_version,
        "policy_version": policy_version,
        "ranking_profile": "hybrid-v2",
        "source_manifest": str(manifest_path),
        "source_manifest_sha256": manifest_sha256,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    from KB.index_compatibility import validate_collection_metadata
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        collection = client.get_or_create_collection(collection_name, metadata=metadata)
    else:
        validate_collection_metadata(
            collection.metadata or {},
            model=model,
            schema_version=schema_version,
            policy_version=policy_version,
            manifest_path=str(manifest_path),
            manifest_sha256=manifest_sha256,
        )

    # Chroma collection metadata is immutable after creation; keep the existing
    # collection's verified metadata and only use it for compatibility checks.

    vector_count = 0
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    for batch_number, batch in enumerate(_batch(chunks, batch_size), 1):
        texts = [str(item["text"]) for item in batch]
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                vectors = embedder.embed_documents(texts)
                break
            except Exception as error:
                last_error = error
                if attempt == max_retries:
                    raise RuntimeError(
                        f"embedding batch {batch_number}/{total_batches} failed after {max_retries} attempts"
                    ) from error
        else:
            raise RuntimeError("embedding failed") from last_error
        collection.upsert(
            ids=[str(item["chunk_id"]) for item in batch],
            embeddings=vectors,
            documents=texts,
            metadatas=[
                {
                    "source_id": str(item.get("source_id", "")),
                    "path": str(item.get("path", "")),
                    "ordinal": int(item.get("ordinal", 0)),
                    "content_hash": str(item.get("content_hash", "")),
                    "source_version_id": str(item.get("source_version_id", "")),
                    "document_id": str(item.get("document_id", "")),
                    "title": str(item.get("title", "")),
                    "locator": str(item.get("locator", item.get("path", ""))),
                    "source_type": str(item.get("source_type", "unknown")),
                    "content_class": str(item.get("content_class", "unknown")),
                    "environment_scope": str(item.get("environment_scope", "unknown")),
                    "is_approved": bool(item.get("is_approved", False)),
                    "is_unsafe": bool(item.get("is_unsafe", True)),
                    "trust_level": int(item.get("trust_level", 0)),
                    "policy_tags": str(item.get("policy_tags", "[]")),
                    "metadata_schema_version": str(item.get("assessment_metadata_schema_version", item.get("metadata_schema_version", "workflow-metadata-v1"))),
                    "assessment_phase": str(item.get("assessment_phase", "")),
                    "reporting_class": str(item.get("reporting_class", "")),
                    "identity_class": str(item.get("identity_class", "")),
                    "authorization_class": str(item.get("authorization_class", "")),
                    "api_class": str(item.get("api_class", "")),
                }
                for item in batch
            ],
        )
        vector_count += len(batch)
        if progress_path is not None:
            progress_path = Path(progress_path)
            progress_path.parent.mkdir(parents=True, exist_ok=True)
            progress_path.write_text(
                json.dumps({
                    "collection_name": collection_name,
                    "completed_batches": batch_number,
                    "total_batches": total_batches,
                    "vector_count": vector_count,
                    "status": "running",
                }, indent=2),
                encoding="utf-8",
            )

    receipt = {
        "receipt_type": "redsage_v3_workflow_cohere_index",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "manifest_sha256": hashlib.sha256(
            Path(manifest_path).read_bytes()
        ).hexdigest(),
        "collection_name": collection_name,
        "vector_count": vector_count,
        "batch_size": batch_size,
        "index_profile": getattr(embedder, "index_profile", {}),
        "embedding_status": "indexed",
        "metadata_schema_version": schema_version,
        "policy_version": policy_version,
        "ranking_profile": "hybrid-v2",
        "source_manifest_sha256": manifest_sha256,
    }
    if receipt_path is not None:
        receipt_path = Path(receipt_path)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
