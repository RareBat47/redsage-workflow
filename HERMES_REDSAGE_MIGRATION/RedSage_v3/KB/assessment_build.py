"""Build a pre-embedding manifest for KB-02 Web App assessment guidance."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from typing import Any
from KB.assessment_sources import select_assessment_sources
from KB.workflow_corpus import chunk_text, read_text_file
from KB.workflow_build import enrich_source_metadata

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _phase(path: str, text: str = "") -> str:
    lower = f"{path} {text}".lower()
    if any(term in lower for term in ("authorization", "access_control", "idor", "bola", "privilege escalation", "object-level")):
        return "authorization"
    if any(term in lower for term in ("authentication", "session", "oauth", "jwt", "login", "identity", "cookie")):
        return "identity_session"
    if any(term in lower for term in ("injection", "input_validation", "xss", "csrf", "deserialization", "upload")):
        return "input_validation"
    if any(term in lower for term in ("business logic", "workflow", "state transition", "race condition")):
        return "business_logic"
    if any(term in lower for term in ("api", "rest", "graphql", "websocket")):
        return "api_context"
    if any(term in lower for term in ("information_gathering", "attack_surface", "http", "browser", "configuration")):
        return "application_context"
    if any(term in lower for term in ("scope", "stop", "escalation", "authorization gate")):
        return "scope_safety"
    if any(term in lower for term in ("cwe", "cvss", "report", "evidence", "remediation", "finding")):
        return "evidence_reporting"
    return "assessment_general"

def build_assessment_preview(resources_root: str | Path, output_path: str | Path, *, max_chars: int = 2200) -> dict[str, Any]:
    root, output = Path(resources_root), Path(output_path)
    sources, chunks = [], []
    for path in select_assessment_sources(root):
        relative = path.relative_to(root).as_posix()
        text, file_hash = read_text_file(path), _sha256(path)
        metadata = enrich_source_metadata(Path(relative), file_hash)
        metadata.update({"assessment_phase": _phase(relative, text), "assessment_metadata_schema_version": "assessment-v1"})
        records = chunk_text(text, max_chars=max_chars, overlap=min(250, max_chars // 5), source_path=relative)
        source_id = metadata["document_id"]
        sources.append({"source_id": source_id, "path": relative, "bytes": path.stat().st_size, "sha256": file_hash, "metadata": metadata, "chunk_count": len(records)})
        for record in records:
            chunks.append({"chunk_id": f"{source_id}:{record.ordinal}", "source_id": source_id, "path": relative, "ordinal": record.ordinal, "content_hash": record.content_hash, "char_count": len(record.text), "text": record.text, **metadata})
    manifest = {"manifest_type": "redsage_v3_assessment_kb_preview", "created_at": datetime.now(timezone.utc).isoformat(), "resources_root": root.as_posix(), "source_count": len(sources), "chunk_count": len(chunks), "embedding_status": "not_embedded", "collection_name": "redsage_v3_assessment_web_cohere_v1", "sources": sources, "chunks": chunks}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("resources_root")
    parser.add_argument("output_path")
    args = parser.parse_args()
    data = build_assessment_preview(args.resources_root, args.output_path)
    print(json.dumps({k: data[k] for k in ("source_count", "chunk_count", "embedding_status", "collection_name")}, indent=2))
