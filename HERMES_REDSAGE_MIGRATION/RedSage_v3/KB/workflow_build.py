"""Build a pre-embedding workflow KB manifest from selected source files."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Any

from KB.workflow_corpus import chunk_text, read_text_file, source_id_for_path
from KB.workflow_sources import select_workflow_sources


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def enrich_source_metadata(path: Path, file_hash: str) -> dict[str, object]:
    relative = str(path).replace("\\", "/")
    if relative.startswith("03_owasp/"):
        source_type, scope, approved, unsafe, trust = "owasp", "authorized_engagement", True, False, 4
        policy_tags = ["web_application", "reference"]
    elif relative.startswith("04_cwe_cvss/"):
        source_type, scope, approved, unsafe, trust = "taxonomy", "authorized_engagement", True, False, 4
        policy_tags = ["taxonomy", "severity"]
    elif relative.startswith("05_web_platform_docs/"):
        source_type, scope, approved, unsafe, trust = "technology_reference", "authorized_engagement", True, False, 3
        policy_tags = ["web_application", "technology"]
    elif relative.startswith("09_scope_authorization/"):
        source_type, scope, approved, unsafe, trust = "redsage_policy", "authorized_engagement", True, False, 5
        policy_tags = ["authorization", "scope"]
    elif relative.startswith("10_stop_escalation/"):
        source_type, scope, approved, unsafe, trust = "redsage_policy", "authorized_engagement", True, False, 5
        policy_tags = ["stop_condition", "escalation"]
    elif relative.startswith("08_lab_ctf/"):
        source_type, scope, approved, unsafe, trust = "lab", "lab_only", True, False, 2
        policy_tags = ["lab"]
    elif relative.startswith("01_methodology_book/"):
        source_type, scope, approved, unsafe, trust = "methodology", "authorized_engagement", False, False, 3
        policy_tags = ["methodology", "rights_review_required"]
    elif relative.startswith("02_redsage_domain/"):
        source_type, scope, approved, unsafe, trust = "redsage_domain", "authorized_engagement", True, False, 5
        policy_tags = ["redsage", "workflow"]
    else:
        source_type, scope, approved, unsafe, trust = "unknown", "unknown", False, True, 0
        policy_tags = ["review_required"]
    stem = Path(relative).stem or "source"
    return {
        "source_type": source_type,
        "content_class": "policy" if source_type == "redsage_policy" else "reference",
        "environment_scope": scope,
        "is_approved": approved,
        "is_unsafe": unsafe,
        "trust_level": trust,
        "policy_tags": json.dumps(policy_tags),
        "source_version_id": _stable_id("version", file_hash),
        "document_id": _stable_id("document", relative + file_hash),
        "title": stem.replace("_", " ").replace("-", " ").strip().title(),
        "locator": relative,
        "metadata_schema_version": "workflow-metadata-v1",
    }


def build_preview_manifest(
    resources_root: str | Path,
    output_path: str | Path,
    *,
    max_chars: int = 2200,
    overlap: int | None = None,
) -> dict[str, Any]:
    resources_root = Path(resources_root)
    output_path = Path(output_path)
    if overlap is None:
        overlap = min(250, max(0, max_chars // 5))
    selected = select_workflow_sources(resources_root)

    sources: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    for source_path in selected:
        rel = source_path.relative_to(resources_root).as_posix()
        text = read_text_file(source_path)
        source_id = source_id_for_path(rel)
        file_hash = _sha256_file(source_path)
        source_metadata = enrich_source_metadata(Path(rel), file_hash)
        records = chunk_text(text, max_chars=max_chars, overlap=overlap, source_path=rel)
        sources.append(
            {
                "source_id": source_id,
                "path": rel,
                "bytes": source_path.stat().st_size,
                "sha256": file_hash,
                "metadata": source_metadata,
                "chunk_count": len(records),
            }
        )
        for record in records:
            chunks.append(
                {
                    "chunk_id": f"{source_id}:{record.ordinal}",
                    "source_id": source_id,
                    "path": rel,
                    "ordinal": record.ordinal,
                    "content_hash": record.content_hash,
                    "char_count": len(record.text),
                    "text": record.text,
                    **source_metadata,
                }
            )

    manifest: dict[str, Any] = {
        "manifest_type": "redsage_v3_workflow_kb_preview",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resources_root": resources_root.as_posix(),
        "source_count": len(sources),
        "chunk_count": len(chunks),
        "embedding_status": "not_embedded",
        "collection_name": "redsage_v3_workflow_cohere_v1",
        "sources": sources,
        "chunks": chunks,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("resources_root")
    parser.add_argument("output_path")
    parser.add_argument("--max-chars", type=int, default=2200)
    args = parser.parse_args()
    result = build_preview_manifest(args.resources_root, args.output_path, max_chars=args.max_chars)
    print(json.dumps({k: result[k] for k in ["source_count", "chunk_count", "embedding_status"]}, indent=2))
