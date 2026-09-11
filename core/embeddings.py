"""Embedding providers matching the models that built the existing KB vectors.

The active collection (redsage_kb_local_v4) was built with the offline
DeterministicEmbedder: SHA-256 of the text, first 8 bytes scaled to [0, 1].
That algorithm is reproduced exactly here so existing vectors stay compatible.
"""

import hashlib
import os
from importlib import import_module
from typing import Protocol

from core.config import settings


class Embedder(Protocol):
    provider_name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, texts: list[str]) -> list[list[float]]: ...


class DeterministicEmbedder:
    provider_name = "local"

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vectors.append([byte / 255 for byte in digest[:8]])
        return vectors

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        return self.embed(texts)


class CohereEmbedder:
    """Optional provider for future re-ingestion (embed-english-v3.0, 1024 dims).

    Requires the `cohere` package and CO_API_KEY / COHERE_API_KEY.
    The preserved collections built with this provider are historical.
    """

    provider_name = "cohere"

    def __init__(self) -> None:
        cohere = import_module("cohere")
        self._client = cohere.Client(
            api_key=os.getenv("CO_API_KEY") or os.environ["COHERE_API_KEY"]
        )
        self._model = settings.cohere_embed_model

    def _embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        response = self._client.embed(
            texts=texts,
            model=self._model,
            input_type=input_type,
            embedding_types=["float"],
        )
        embeddings = getattr(response, "embeddings", response)
        if isinstance(embeddings, dict):
            embeddings = embeddings.get("float", [])
        else:
            embeddings = getattr(embeddings, "float_", embeddings)
        return [[float(value) for value in vector] for vector in embeddings]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "search_document")

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "search_query")


def cohere_configured() -> bool:
    return bool(os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY"))


def load_embedder(provider: str | None = None) -> DeterministicEmbedder | CohereEmbedder:
    provider = provider or settings.embedding_provider
    if provider == "cohere" and cohere_configured():
        return CohereEmbedder()
    return DeterministicEmbedder()
