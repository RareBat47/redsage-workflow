"""Cohere embedding adapter for the governed workflow KB."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv

# Resolve the project .env regardless of the process working directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_PROJECT_ROOT / ".env")


class CohereEmbeddingAdapter:
    def __init__(
        self,
        *,
        model: str = "embed-english-v3.0",
        api_key: str | None = None,
        client: Any | None = None,
        dimensions: int | None = None,
    ) -> None:
        self.model = model
        self._api_key = api_key or os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY")
        if client is None:
            if not self._api_key:
                raise RuntimeError("Cohere API key is not configured")
            import cohere

            client = cohere.ClientV2(api_key=self._api_key)
        self.client = client
        self.dimensions = dimensions

    @property
    def index_profile(self) -> dict[str, object]:
        return {
            "provider": "cohere",
            "model": self.model,
            "document_input_type": "search_document",
            "query_input_type": "search_query",
            "dimensions": self.dimensions,
        }

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._embed(texts, "search_document")

    def embed_query(self, text: str) -> list[float]:
        vectors = self._embed([text], "search_query")
        if len(vectors) != 1:
            raise RuntimeError("Cohere returned an unexpected query embedding count")
        return vectors[0]

    def _embed(self, texts: Sequence[str], input_type: str) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embed(
            model=self.model,
            input_type=input_type,
            texts=list(texts),
            embedding_types=["float"],
        )
        vectors = extract_float_embeddings(response)
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Cohere returned {len(vectors)} embeddings for {len(texts)} texts"
            )
        if self.dimensions is None:
            self.dimensions = len(vectors[0]) if vectors else None
        elif any(len(vector) != self.dimensions for vector in vectors):
            raise RuntimeError("Cohere embedding dimensions changed within a batch")
        return vectors


def extract_float_embeddings(response: Any) -> list[list[float]]:
    embeddings = getattr(response, "embeddings", response)
    if isinstance(embeddings, dict):
        embeddings = embeddings.get("float", embeddings.get("float_", []))
    else:
        embeddings = getattr(embeddings, "float_", embeddings)
    return [[float(value) for value in vector] for vector in embeddings]
