"""Build KB-06 evidence/reporting embeddings after preview approval."""
from __future__ import annotations
from pathlib import Path
import json
from KB.cohere_index import build_cohere_index

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = build_cohere_index(
        root / "data" / "kb_build" / "reporting_preview_manifest.json",
        collection_name="redsage_v3_evidence_reporting_cohere_v1",
        batch_size=96,
        receipt_path=root / "data" / "kb_build" / "evidence_reporting_cohere_v1_receipt.json",
        progress_path=root / "data" / "kb_build" / "evidence_reporting_cohere_v1_progress.json",
    )
    print(json.dumps(result, indent=2))
