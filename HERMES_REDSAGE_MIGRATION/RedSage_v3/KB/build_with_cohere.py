"""CLI entry point for the approved Cohere workflow KB build."""

from __future__ import annotations

from pathlib import Path
import json

from KB.cohere_index import build_cohere_index


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    manifest = root / "data" / "kb_build" / "workflow_preview_manifest.json"
    receipt = root / "data" / "kb_build" / "workflow_cohere_v1_receipt.json"
    result = build_cohere_index(
        manifest,
        collection_name="redsage_v3_workflow_cohere_v1",
        batch_size=96,
        receipt_path=receipt,
        progress_path=root / "data" / "kb_build" / "workflow_cohere_v1_progress.json",
    )
    print(json.dumps(result, indent=2))
