"""Reconcile current manifests, build receipts, and live collection IDs."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from KB.index_compatibility import validate_collection_ids  # noqa: E402

SPECS = (
    ("workflow", "workflow_preview_manifest.json", "workflow_cohere_v1_receipt.json", "redsage_v3_workflow_cohere_v1"),
    ("assessment_web", "assessment_web_preview_manifest.json", "assessment_web_cohere_v1_receipt.json", "redsage_v3_assessment_web_cohere_v1"),
    ("evidence_reporting", "reporting_preview_manifest.json", "evidence_reporting_cohere_v1_receipt.json", "redsage_v3_evidence_reporting_cohere_v1"),
    ("identity", "identity_preview_manifest.json", "identity_cohere_v1_receipt.json", "redsage_v3_assessment_identity_cohere_v1"),
    ("authorization", "authorization_preview_manifest.json", "authorization_cohere_v1_receipt.json", "redsage_v3_assessment_authorization_cohere_v1"),
    ("api", "api_preview_manifest.json", "api_cohere_v1_receipt.json", "redsage_v3_assessment_api_cohere_v1"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile() -> dict[str, Any]:
    import chromadb
    chroma = chromadb.PersistentClient(path=str(ROOT / "data" / "kb_build" / "chroma"))
    rows = []
    for domain, manifest_name, receipt_name, collection_name in SPECS:
        manifest_path = ROOT / "data" / "kb_build" / manifest_name
        receipt_path = ROOT / "data" / "kb_build" / receipt_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        collection = chroma.get_collection(collection_name)
        ids = validate_collection_ids(manifest, collection)
        current_hash = sha256(manifest_path)
        rows.append({
            "domain": domain,
            "manifest": str(manifest_path),
            "manifest_sha256": current_hash,
            "build_receipt_sha256": receipt.get("manifest_sha256"),
            "receipt_hash_matches_current": receipt.get("manifest_sha256") == current_hash,
            "collection_name": collection_name,
            "manifest_chunk_count": manifest["chunk_count"],
            "collection_vector_count": collection.count(),
            "stale_ids": len(ids["stale_ids"]),
            "missing_ids": len(ids["missing_ids"]),
            "status": "verified_current_manifest" if receipt.get("manifest_sha256") == current_hash else "verified_ids_hash_changed_since_build",
        })
    result = {"receipt_type": "redsage_v3_kb_integrity_reconciliation", "created_at": datetime.now(timezone.utc).isoformat(), "domains": rows, "all_counts_consistent": all(r["stale_ids"] == 0 and r["missing_ids"] == 0 and r["manifest_chunk_count"] == r["collection_vector_count"] for r in rows)}
    out = ROOT / "data" / "kb_build" / "integrity_reconciliation_receipt.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(reconcile(), indent=2))
