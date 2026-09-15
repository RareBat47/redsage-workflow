"""Inspect selected workflow sources before Cohere indexing."""

from __future__ import annotations

from pathlib import Path
import json

from KB.workflow_build import build_preview_manifest


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "RESOURCES" / "WORKFLOW_GENERATION"
    output = Path(__file__).resolve().parents[1] / "data" / "kb_build" / "workflow_preview_manifest.json"
    result = build_preview_manifest(root, output)
    summary = {
        "source_count": result["source_count"],
        "chunk_count": result["chunk_count"],
        "embedding_status": result["embedding_status"],
        "manifest": str(output),
    }
    print(json.dumps(summary, indent=2))
