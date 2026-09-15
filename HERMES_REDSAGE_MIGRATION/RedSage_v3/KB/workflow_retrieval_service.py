"""Bounded retrieval over the Cohere workflow KB with citations and receipts."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from KB.cohere_embeddings import CohereEmbeddingAdapter
from KB.retrieval import classify_query, rank_chunks
from KB.receipts import write_retrieval_receipt
from KB.policies import filter_chunks
from KB.citations import assemble_citations


def _source_type(path: str) -> str:
    if path.startswith("08_lab_ctf/"):
        return "lab"
    if path.startswith(("09_scope_authorization/", "10_stop_escalation/")):
        return "redsage_policy"
    if path.startswith("03_owasp/"):
        return "owasp"
    if path.startswith("04_cwe_cvss/"):
        return "taxonomy"
    return "reference"


def search_workflow_context(
    query: str,
    *,
    chroma_path: str | Path = "data/kb_build/chroma",
    collection_name: str = "redsage_v3_workflow_cohere_v1",
    environment_scope: str = "authorized_engagement",
    top_k: int = 8,
    actor_type: str = "operator",
    receipt_directory: str | Path = "data/kb_build/retrieval_receipts",
    embedder: Any | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query is required")
    if environment_scope not in {"authorized_engagement", "lab_only"}:
        raise ValueError("unsupported environment_scope")
    if embedder is None:
        embedder = CohereEmbeddingAdapter()
    if client is None:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_path))
    col = client.get_collection(collection_name)
    query_vector = embedder.embed_query(query)
    response = col.query(query_embeddings=[query_vector], n_results=max(top_k * 3, top_k), include=["documents", "metadatas", "distances"])
    candidates=[]
    for chunk_id,text,metadata,distance in zip(response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]):
        path = str(metadata.get("path", ""))
        source_type = str(metadata.get("source_type") or _source_type(path))
        normalized = {
            "chunk_id": chunk_id,
            "text": text,
            "path": path,
            "ordinal": metadata.get("ordinal", 0),
            "source_id": metadata.get("source_id", ""),
            "content_hash": metadata.get("content_hash", ""),
            "source_version_id": metadata.get("source_version_id", ""),
            "document_id": metadata.get("document_id", ""),
            "title": metadata.get("title", ""),
            "locator": metadata.get("locator", path),
            "source_type": source_type,
            "content_class": metadata.get("content_class", "unknown"),
            "environment_scope": metadata.get("environment_scope", "lab_only" if source_type == "lab" else "authorized_engagement"),
            "is_approved": metadata.get("is_approved", True),
            "is_unsafe": metadata.get("is_unsafe", False),
            "trust_level": metadata.get("trust_level", 0),
            "policy_tags": metadata.get("policy_tags", "[]"),
            "vector_score": max(0.0, 1.0 - float(distance)),
        }
        candidates.append(normalized)
    classification = classify_query(query)
    candidate_count = len(candidates)
    candidates = filter_chunks(
        candidates,
        environment_scope=environment_scope,
        tenant_id=None,
        include_lab=False,
    )
    ranked=rank_chunks(query,candidates)[:top_k]
    citations=assemble_citations([{"citation_id":f"[{i}]","chunk_id":item["chunk_id"],"source_id":item["source_id"],"source_version_id":item["source_version_id"],"document_id":item["document_id"],"title":item["title"],"path":item["path"],"locator":item["locator"],"source_type":item["source_type"],"trust_level":item["trust_level"],"is_approved":item["is_approved"],"excerpt":item["text"][:600],"score":round(item["score"],4),"score_components":item["score_components"],"content_hash":item["content_hash"]} for i,item in enumerate(ranked,1)])
    filtered_count = candidate_count - len(candidates)
    warnings = [] if not filtered_count else [f"{filtered_count} candidate(s) filtered by workflow KB policy"]
    receipt=write_retrieval_receipt(receipt_directory,actor_type=actor_type,index_profile="cohere/embed-english-v3.0:1024",policy_version="workflow-v1",selected_chunk_ids=[x["chunk_id"] for x in citations],score_components={x["chunk_id"]:x["score_components"] for x in citations},query=query,warnings=warnings)
    return {"query_id":receipt["query_id"],"retrieval_timestamp":datetime.now(timezone.utc).isoformat(),"environment_scope":environment_scope,"query_classification":classification,"candidate_count":candidate_count,"filtered_count":filtered_count,"citations":citations,"warnings":warnings}
