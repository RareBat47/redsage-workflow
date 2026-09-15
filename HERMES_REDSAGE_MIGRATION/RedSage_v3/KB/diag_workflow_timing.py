"""Time each phase of the internal engagement workflow to locate stalls."""
from __future__ import annotations

import time


def log(label: str, start: float) -> float:
    now = time.perf_counter()
    print(f"[diag] {label}: {now - start:.2f}s", flush=True)
    return now


PROBLEM = (
    "Authorized web application assessment of authentication, session "
    "management, and object-level authorization."
)

print(f"[diag] python pid ready", flush=True)
t0 = time.perf_counter()

from KB.consolidated_retrieval import KBProfile, search_consolidated  # noqa: E402
t1 = log("import KB.consolidated_retrieval", t0)

PROFILES = [
    KBProfile("redsage_v3_workflow_cohere_v1", "workflow", "workflow-v1"),
    KBProfile("redsage_v3_assessment_web_cohere_v1", "assessment", "assessment-v1"),
    KBProfile("redsage_v3_evidence_reporting_cohere_v1", "reporting", "reporting-v1"),
    KBProfile("redsage_v3_assessment_identity_cohere_v1", "identity", "assessment-v1"),
    KBProfile("redsage_v3_assessment_authorization_cohere_v1", "authorization", "assessment-v1"),
    KBProfile("redsage_v3_assessment_api_cohere_v1", "api", "assessment-v1"),
]

from KB.cohere_embeddings import CohereEmbeddingAdapter  # noqa: E402
t2 = log("import CohereEmbeddingAdapter", t1)

adapter = CohereEmbeddingAdapter()
t3 = log("construct CohereEmbeddingAdapter", t2)

vector = adapter.embed_query(PROBLEM)
t4 = log(f"embed_query (dim={len(vector)})", t3)

import chromadb  # noqa: E402

client = chromadb.PersistentClient(path="data/kb_build/chroma")
t5 = log("chromadb.PersistentClient", t4)

for profile in PROFILES:
    col = client.get_collection(profile.collection_name)
    t6 = time.perf_counter()
    col.query(query_embeddings=[vector], n_results=5, include=["documents", "metadatas", "distances"])
    t5 = log(f"query {profile.kb_domain} (shared client)", t6)

t7 = time.perf_counter()
result = search_consolidated(PROBLEM, profiles=PROFILES, top_k=5)
log(f"search_consolidated -> {len(result['citations'])} citations", t7)

print("[diag] DONE", flush=True)