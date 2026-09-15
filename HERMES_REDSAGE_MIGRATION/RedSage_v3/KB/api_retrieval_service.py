"""API-specific retrieval over the internal API assessment KB."""
from __future__ import annotations
from typing import Any
from KB.assessment_retrieval_service import search_assessment_kb


def search_api_kb(query: str, *, top_k: int = 8, **kwargs: Any) -> dict[str, Any]:
    result = search_assessment_kb(
        f"API REST schema validation rate limiting object authorization {query}",
        collection_name="redsage_v3_assessment_api_cohere_v1",
        top_k=top_k,
        **kwargs,
    )
    result["kb_domain"] = "api_assessment"
    return result
