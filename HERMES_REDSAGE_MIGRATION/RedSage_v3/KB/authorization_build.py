"""Select and preview authorization/business-logic guidance for KB-05."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from typing import Any
from KB.workflow_corpus import chunk_text, read_text_file
from KB.workflow_build import enrich_source_metadata
from KB.workflow_sources import is_selectable_workflow_source

_INCLUDE = ("authorization", "access_control", "idor", "insecure_direct_object", "object_level", "bola", "business_logic", "business-logic", "integrity_checks", "workflow")
_EXCLUDE = ("authentication", "session", "oauth", "jwt", "cookie")

def select_authorization_sources(root: str | Path) -> list[Path]:
    root = Path(root)
    selected = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_selectable_workflow_source(path):
            continue
        relative = path.relative_to(root).as_posix().lower()
        if not relative.startswith(("03_owasp/", "04_cwe_cvss/", "02_redsage_domain/", "09_scope_authorization/", "10_stop_escalation/")):
            continue
        if any(term in relative for term in _EXCLUDE):
            continue
        if any(term in relative for term in _INCLUDE):
            selected.append(path)
    return sorted(selected)

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _classify(path: str, text: str) -> str:
    value = f"{path} {text}".lower()
    if any(term in value for term in ("business logic", "business_logic", "integrity", "workflow", "state transition", "race condition")):
        return "business_logic"
    if any(term in value for term in ("idor", "object", "bola", "direct object")):
        return "object_access"
    if any(term in value for term in ("scope", "stop", "escalation")):
        return "scope_safety"
    return "access_control"

def build_authorization_preview(resources_root: str | Path, output_path: str | Path, *, max_chars: int = 2200) -> dict[str, Any]:
    root, output = Path(resources_root), Path(output_path)
    sources, chunks = [], []
    for path in select_authorization_sources(root):
        relative = path.relative_to(root).as_posix()
        text, file_hash = read_text_file(path), _sha256(path)
        metadata = enrich_source_metadata(Path(relative), file_hash)
        metadata.update({"authorization_class": _classify(relative, text), "authorization_metadata_schema_version": "authorization-v1"})
        records = chunk_text(text, max_chars=max_chars, overlap=min(250, max_chars // 5), source_path=relative)
        source_id = metadata["document_id"]
        sources.append({"source_id": source_id, "path": relative, "bytes": path.stat().st_size, "sha256": file_hash, "metadata": metadata, "chunk_count": len(records)})
        for record in records:
            chunks.append({"chunk_id": f"{source_id}:{record.ordinal}", "source_id": source_id, "path": relative, "ordinal": record.ordinal, "content_hash": record.content_hash, "char_count": len(record.text), "text": record.text, **metadata})
    manifest = {"manifest_type": "redsage_v3_authorization_kb_preview", "created_at": datetime.now(timezone.utc).isoformat(), "resources_root": root.as_posix(), "source_count": len(sources), "chunk_count": len(chunks), "embedding_status": "not_embedded", "collection_name": "redsage_v3_assessment_authorization_cohere_v1", "sources": sources, "chunks": chunks}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("resources_root")
    parser.add_argument("output_path")
    args = parser.parse_args()
    data = build_authorization_preview(args.resources_root, args.output_path)
    print(json.dumps({k: data[k] for k in ("source_count", "chunk_count", "embedding_status", "collection_name")}, indent=2))
