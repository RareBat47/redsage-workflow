"""Build a preview manifest for the evidence/reporting KB domain."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from typing import Any
from KB.workflow_corpus import chunk_text, read_text_file
from KB.workflow_build import enrich_source_metadata
from KB.workflow_sources import is_selectable_workflow_source

_REPORTING_TERMS = ("evidence", "finding", "report", "remediation", "severity", "reproduction", "cvss", "cwe", "logging", "disclosure")
_EXCLUDE_TERMS = ("authorization", "authentication", "session", "injection", "attack_surface")

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _reporting_class(path: str, text: str) -> str:
    value = f"{path} {text}".lower()
    if any(term in value for term in ("cvss", "severity")):
        return "severity"
    if any(term in value for term in ("evidence", "logging")):
        return "evidence"
    if any(term in value for term in ("remediation", "prevention", "mitigation")):
        return "remediation"
    if any(term in value for term in ("finding", "reproduction", "disclosure", "report")):
        return "finding_reporting"
    return "reporting_general"

def build_reporting_preview(resources_root: str | Path, output_path: str | Path, *, max_chars: int = 2200) -> dict[str, Any]:
    root, output = Path(resources_root), Path(output_path)
    sources, chunks = [], []
    for path in root.rglob("*"):
        if not path.is_file() or not is_selectable_workflow_source(path):
            continue
        relative = path.relative_to(root).as_posix()
        text = read_text_file(path)
        value = f"{relative} {text}".lower()
        if not any(term in value for term in _REPORTING_TERMS):
            continue
        if relative.startswith("03_owasp/wstg/") and any(term in relative.lower() for term in _EXCLUDE_TERMS):
            continue
        file_hash = _sha256(path)
        metadata = enrich_source_metadata(Path(relative), file_hash)
        metadata.update({"reporting_class": _reporting_class(relative, text), "reporting_metadata_schema_version": "reporting-v1"})
        records = chunk_text(text, max_chars=max_chars, overlap=min(250, max_chars // 5), source_path=relative)
        source_id = metadata["document_id"]
        sources.append({"source_id": source_id, "path": relative, "bytes": path.stat().st_size, "sha256": file_hash, "metadata": metadata, "chunk_count": len(records)})
        for record in records:
            chunks.append({"chunk_id": f"{source_id}:{record.ordinal}", "source_id": source_id, "path": relative, "ordinal": record.ordinal, "content_hash": record.content_hash, "char_count": len(record.text), "text": record.text, **metadata})
    manifest = {"manifest_type": "redsage_v3_reporting_kb_preview", "created_at": datetime.now(timezone.utc).isoformat(), "resources_root": root.as_posix(), "source_count": len(sources), "chunk_count": len(chunks), "embedding_status": "not_embedded", "collection_name": "redsage_v3_evidence_reporting_cohere_v1", "sources": sources, "chunks": chunks}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
