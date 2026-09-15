"""Prepare the isolated lab/CTF reasoning KB without mixing it into engagements."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from typing import Any
from KB.workflow_corpus import chunk_text, read_text_file
from KB.workflow_sources import is_selectable_workflow_source


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def select_lab_sources(root: str | Path) -> list[Path]:
    root = Path(root)
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and is_selectable_workflow_source(path)
        and path.relative_to(root).as_posix().startswith("08_lab_ctf/")
    )


def build_lab_preview(resources_root: str | Path, output_path: str | Path, *, max_chars: int = 2200) -> dict[str, Any]:
    root, output = Path(resources_root), Path(output_path)
    sources, chunks = [], []
    for path in select_lab_sources(root):
        relative = path.relative_to(root).as_posix()
        text, file_hash = read_text_file(path), _sha256(path)
        source_id = "lab_" + hashlib.sha256((relative + file_hash).encode()).hexdigest()[:16]
        records = chunk_text(text, max_chars=max_chars, overlap=min(250, max_chars // 5), source_path=relative)
        metadata = {
            "source_type": "lab",
            "content_class": "lab_reasoning",
            "environment_scope": "lab_only",
            "is_approved": True,
            "is_unsafe": False,
            "trust_level": 2,
            "policy_tags": json.dumps(["lab", "downrank_default"]),
            "source_version_id": "version_" + file_hash[:16],
            "document_id": source_id,
            "title": path.stem.replace("_", " ").title(),
            "locator": relative,
            "lab_metadata_schema_version": "lab-v1",
        }
        sources.append({"source_id": source_id, "path": relative, "bytes": path.stat().st_size, "sha256": file_hash, "metadata": metadata, "chunk_count": len(records)})
        for record in records:
            chunks.append({"chunk_id": f"{source_id}:{record.ordinal}", "source_id": source_id, "path": relative, "ordinal": record.ordinal, "content_hash": record.content_hash, "char_count": len(record.text), "text": record.text, **metadata})
    manifest = {"manifest_type": "redsage_v3_lab_kb_preview", "created_at": datetime.now(timezone.utc).isoformat(), "resources_root": root.as_posix(), "source_count": len(sources), "chunk_count": len(chunks), "embedding_status": "not_embedded", "collection_name": "redsage_v3_lab_cohere_v1", "sources": sources, "chunks": chunks}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
