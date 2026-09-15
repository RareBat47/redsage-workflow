"""Consolidated, policy-first retrieval across RedSage KB profiles."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
import time

from KB.citations import assemble_citations
from KB.cohere_embeddings import CohereEmbeddingAdapter
from KB.policies import filter_chunks_with_reasons
from KB.receipts import write_retrieval_receipt
from KB.retrieval import classify_query, rank_chunks


def _query_collection(collection: Any, vector: list[float], n_results: int, attempts: int = 3) -> dict[str, Any]:
    """Retry transient local Chroma segment-reader failures without re-embedding."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return collection.query(
                query_embeddings=[vector],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(0.2 * (attempt + 1))
    raise RuntimeError("local Chroma query failed after retries") from last_error


def _queryable_client(chroma_path: str | Path) -> Any:
    import chromadb
    return chromadb.PersistentClient(path=str(chroma_path))



@dataclass(frozen=True)
class KBProfile:
    collection_name: str
    kb_domain: str
    policy_version: str
    index_profile: str = "cohere/embed-english-v3.0:1024"


def _normalize(chunk_id: str, text: str, metadata: dict[str, Any], distance: float, profile: KBProfile) -> dict[str, Any]:
    metadata = metadata or {}
    source_type = str(metadata.get("source_type") or "unknown")
    return {
        "chunk_id": chunk_id,
        "citation_key": f"{profile.kb_domain}:{chunk_id}",
        "text": text,
        "path": str(metadata.get("path", "")),
        "ordinal": metadata.get("ordinal", 0),
        "source_id": str(metadata.get("source_id", "")),
        "source_version_id": str(metadata.get("source_version_id", "")),
        "document_id": str(metadata.get("document_id", "")),
        "title": str(metadata.get("title", "")),
        "locator": str(metadata.get("locator", metadata.get("path", ""))),
        "content_hash": str(metadata.get("content_hash", "")),
        "source_type": source_type,
        "content_class": str(metadata.get("content_class", "unknown")),
        "environment_scope": str(metadata.get("environment_scope", "unknown")),
        "is_approved": metadata.get("is_approved", False),
        "is_unsafe": metadata.get("is_unsafe", True),
        "trust_level": metadata.get("trust_level", 0),
        "policy_tags": metadata.get("policy_tags", "[]"),
        "assessment_phase": str(metadata.get("assessment_phase", "")),
        "reporting_class": str(metadata.get("reporting_class", "")),
        "identity_class": str(metadata.get("identity_class", "")),
        "authorization_class": str(metadata.get("authorization_class", "")),
        "api_class": str(metadata.get("api_class", "")),
        "kb_domain": profile.kb_domain,
        "policy_version": profile.policy_version,
        "vector_score": max(0.0, 1.0 - float(distance)),
    }


def search_consolidated(query: str, *, profiles: Sequence[KBProfile], chroma_path: str | Path = "data/kb_build/chroma", environment_scope: str = "authorized_engagement", top_k: int = 8, actor_type: str = "operator", receipt_directory: str | Path = "data/kb_build/consolidated_retrieval_receipts", embedder: Any | None = None, client: Any | None = None) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query is required")
    if not profiles:
        raise ValueError("at least one KB profile is required")
    if not 1 <= top_k <= 25:
        raise ValueError("top_k must be between 1 and 25")
    if embedder is None:
        embedder = CohereEmbeddingAdapter()
    if client is None:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_path))
    vector = embedder.embed_query(query)
    candidates = []
    for profile in profiles:
        # One shared client must serve every collection: creating additional
        # PersistentClient instances over the same path while one is open
        # produces "Error creating hnsw segment reader: Nothing found on disk".
        response = _query_collection(client.get_collection(profile.collection_name), vector, min(25, top_k * 3))
        candidates.extend(_normalize(i, t, m, d, profile) for i, t, m, d in zip(response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]))
    classification = classify_query(query)
    candidate_count = len(candidates)
    candidates, filtered_reasons = filter_chunks_with_reasons(candidates, environment_scope=environment_scope, tenant_id=None, include_lab=False)
    ranked = rank_chunks(query, candidates)[:top_k]
    citations = assemble_citations([{**item, "citation_id": f"[{i}]", "excerpt": item["text"][:600]} for i, item in enumerate(ranked, 1)])
    filtered_count = candidate_count - len(candidates)
    warnings = [] if not filtered_count else [f"{filtered_count} candidate(s) filtered by consolidated KB policy"]
    reason_counts = {reason: filtered_reasons.count(reason) for reason in sorted(set(filtered_reasons))}
    receipt = write_retrieval_receipt(receipt_directory, actor_type=actor_type, index_profile="consolidated:" + ",".join(p.index_profile for p in profiles), policy_version="consolidated-v1", selected_chunk_ids=[x.get("citation_key", x["chunk_id"]) for x in citations], score_components={x.get("citation_key", x["chunk_id"]): x["score_components"] for x in citations}, query=query, warnings=warnings, query_classification=classification["primary"], ranking_profile="hybrid-v2", environment_scope=environment_scope, candidate_count=candidate_count, filtered_count=filtered_count, filtered_reasons=reason_counts)
    return {"query_id": receipt["query_id"], "retrieval_timestamp": datetime.now(timezone.utc).isoformat(), "environment_scope": environment_scope, "query_classification": classification, "candidate_count": candidate_count, "filtered_count": filtered_count, "filtered_reasons": reason_counts, "kb_domains": sorted({x["kb_domain"] for x in citations}), "citations": citations, "warnings": warnings}
