"""Build KB-03 API assessment embeddings with Cohere."""
from __future__ import annotations
from pathlib import Path
import json
from KB.cohere_index import build_cohere_index

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = build_cohere_index(
        root / "data" / "kb_build" / "api_preview_manifest.json",
        collection_name="redsage_v3_assessment_api_cohere_v1",
        batch_size=96,
        receipt_path=root / "data" / "kb_build" / "api_cohere_v1_receipt.json",
        progress_path=root / "data" / "kb_build" / "api_cohere_v1_progress.json",
    )
    print(json.dumps(result, indent=2))
