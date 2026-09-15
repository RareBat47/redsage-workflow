"""Phase-aware retrieval for the internal Web Application assessment KB."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from KB.citations import assemble_citations
from KB.cohere_embeddings import CohereEmbeddingAdapter
from KB.policies import filter_chunks
from KB.receipts import write_retrieval_receipt
from KB.retrieval import classify_query, rank_chunks


def search_assessment_kb(
    query: str,
    *,
    chroma_path: str | Path = "data/kb_build/chroma",
    collection_name: str = "redsage_v3_assessment_web_cohere_v1",
    environment_scope: str = "authorized_engagement",
    top_k: int = 8,
    actor_type: str = "operator",
    receipt_directory: str | Path = "data/kb_build/assessment_retrieval_receipts",
    embedder: Any | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query is required")
    if environment_scope not in {"authorized_engagement", "lab_only"}:
        raise ValueError("unsupported environment_scope")
    if top_k < 1 or top_k > 25:
        raise ValueError("top_k must be between 1 and 25")
    if embedder is None:
        embedder = CohereEmbeddingAdapter()
    if client is None:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_path))
    collection = client.get_collection(collection_name)
    response = collection.query(
        query_embeddings=[embedder.embed_query(query)],
        n_results=min(max(top_k * 3, top_k), 25),
        include=["documents", "metadatas", "distances"],
    )
    candidates = []
    for chunk_id, text, metadata, distance in zip(
        response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]
    ):
        metadata = metadata or {}
        candidates.append({
            "chunk_id": chunk_id,
            "text": text,
            "path": metadata.get("path", ""),
            "ordinal": metadata.get("ordinal", 0),
            "source_id": metadata.get("source_id", ""),
            "source_version_id": metadata.get("source_version_id", ""),
            "document_id": metadata.get("document_id", ""),
            "title": metadata.get("title", ""),
            "locator": metadata.get("locator", metadata.get("path", "")),
            "content_hash": metadata.get("content_hash", ""),
            "source_type": metadata.get("source_type", "unknown"),
            "content_class": metadata.get("content_class", "unknown"),
            "environment_scope": metadata.get("environment_scope", "unknown"),
            "is_approved": metadata.get("is_approved", False),
            "is_unsafe": metadata.get("is_unsafe", True),
            "trust_level": metadata.get("trust_level", 0),
            "policy_tags": metadata.get("policy_tags", "[]"),
            "assessment_phase": metadata.get("assessment_phase", "assessment_general"),
            "vector_score": max(0.0, 1.0 - float(distance)),
        })
    classification = classify_query(query)
    candidate_count = len(candidates)
    candidates = filter_chunks(
        candidates,
        environment_scope=environment_scope,
        tenant_id=None,
        include_lab=False,
    )
    ranked = rank_chunks(query, candidates)[:top_k]
    citation_items = []
    for index, item in enumerate(ranked, 1):
        citation_items.append({
            **item,
            "citation_id": f"[{index}]",
            "excerpt": item["text"][:600],
        })
    citations = assemble_citations(citation_items)
    filtered_count = candidate_count - len(candidates)
    warnings = [] if not filtered_count else [f"{filtered_count} candidate(s) filtered by assessment KB policy"]
    receipt = write_retrieval_receipt(
        receipt_directory,
        actor_type=actor_type,
        index_profile="cohere/embed-english-v3.0:1024",
        policy_version="assessment-v1",
        selected_chunk_ids=[item["chunk_id"] for item in citations],
        score_components={item["chunk_id"]: item["score_components"] for item in citations},
        query=query,
        warnings=warnings,
    )
    return {
        "query_id": receipt["query_id"],
        "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
        "environment_scope": environment_scope,
        "query_classification": classification,
        "candidate_count": candidate_count,
        "filtered_count": filtered_count,
        "citations": citations,
        "warnings": warnings,
    }
