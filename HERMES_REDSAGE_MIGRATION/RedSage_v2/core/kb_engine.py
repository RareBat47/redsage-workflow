"""Decoupled KB search and retrieval over the preserved ChromaDB + SQLite data.

No UI, LLM, or web-framework dependencies: `core` is importable standalone.
Retrieval behavior (lexical rerank, metadata boosts, threshold) is ported
from the original backend so results match the v1 knowledge base.
"""

import ast
import re
import sqlite3
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb

from core.config import settings
from core.embeddings import Embedder, load_embedder


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    title: str
    source: str
    url: str
    text: str
    score: float
    metadata: dict[str, object] | None = None


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in (word.strip(string.punctuation) for word in text.lower().split())
        if token
    }


_STOPWORDS = frozenset(
    "a an and are as at be but by do does for how i in is it its of on or the "
    "to what when where which who why will with you your".split()
)


def _query_tokens(query: str) -> set[str]:
    return {token for token in _tokens(query) if token not in _STOPWORDS}


def lexical_scores(query: str, texts: list[str]) -> list[float]:
    query_words = _query_tokens(query)
    if not query_words:
        return [0.0 for _ in texts]
    scores: list[float] = []
    for text in texts:
        text_words = _tokens(text)
        matches = sum(1 for word in query_words if word in text_words)
        scores.append(matches / len(query_words))
    return scores


def retrieval_hints(query: str) -> dict[str, set[str]]:
    ports = set(re.findall(r"\b(\d{1,5})/(?:tcp|udp)?\b", query.lower()))
    services = {
        term
        for term in (
            "smb",
            "microsoft-ds",
            "ldap",
            "kerberos",
            "winrm",
            "mssql",
            "ms-sql",
            "http",
            "ssh",
            "rdp",
            "ftp",
            "smtp",
            "dns",
        )
        if term in query.lower()
    }
    return {"ports": ports, "services": services}


def _as_set(value: object) -> set[str]:
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            value = [value]
    if isinstance(value, list):
        return {str(item) for item in value}
    return {str(value)}


def metadata_boost(query: str, metadata: object) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    hints = retrieval_hints(query)
    ports = _as_set(metadata.get("ports", []))
    services = {service.lower() for service in _as_set(metadata.get("services", []))}
    title = str(metadata.get("title", "")).lower()
    title_matches = sum(
        service in title or (service == "microsoft-ds" and "smb" in title)
        for service in hints["services"]
    )
    port_matches = sum(port in title for port in hints["ports"])
    source_name = str(metadata.get("source", "")).lower()
    source_boost = 1.0 if source_name == "playbook" or source_name.startswith("playbook:") else 0.0
    trust_level = metadata.get("trust_level", 1)
    try:
        trust_boost = 0.05 * max(0, min(int(trust_level), 4) - 1)
    except (TypeError, ValueError):
        trust_boost = 0.0
    return (
        0.35 * len(hints["ports"] & ports)
        + 0.35 * len(hints["services"] & services)
        + 0.55 * title_matches
        + 0.2 * port_matches
        + source_boost
        + trust_boost
    )


class KBEngine:
    """Self-contained retrieval engine over the preserved KB data."""

    def __init__(
        self,
        chroma_dir: str | Path | None = None,
        db_path: str | Path | None = None,
        collection: str | None = None,
        embedder: Embedder | None = None,
    ) -> None:
        self.chroma_dir = Path(chroma_dir or settings.chroma_dir)
        self.db_path = Path(db_path or settings.sqlite_db)
        self.collection_name = collection or settings.active_collection
        self._embedder = embedder
        self._client: Any = None
        self._collection: Any = None

    @property
    def embedder(self) -> Embedder:
        if self._embedder is None:
            self._embedder = load_embedder()
        return self._embedder

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = chromadb.PersistentClient(path=str(self.chroma_dir))
        return self._client

    def _get_collection(self) -> Any:
        if self._collection is None:
            self._collection = self._get_client().get_collection(self.collection_name)
        return self._collection

    def search(
        self,
        query: str,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> list[Citation]:
        top_k = top_k or settings.top_k
        threshold = settings.score_threshold if threshold is None else threshold
        collection = self._get_collection()
        if collection.count() == 0:
            return []
        result = collection.query(
            query_embeddings=self.embedder.embed_query([query]), n_results=top_k
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        scores = lexical_scores(query, [str(text) for text in documents])
        citations: list[Citation] = []
        for position, text in enumerate(documents):
            metadata = metadatas[position] if position < len(metadatas) else {}
            metadata = metadata if isinstance(metadata, dict) else {}
            score = (
                scores[position] if position < len(scores) else 0.0
            ) + metadata_boost(query, metadata)
            if score >= threshold:
                citations.append(
                    Citation(
                        chunk_id=str(ids[position]),
                        title=str(metadata.get("title", "Untitled")),
                        source=str(metadata.get("source", "Unknown")),
                        url=str(metadata.get("url", "")),
                        text=str(text),
                        score=score,
                        metadata=metadata,
                    )
                )
        return sorted(citations, key=lambda citation: citation.score, reverse=True)

    def collection_stats(self) -> list[dict[str, object]]:
        return [
            {
                "name": collection.name,
                "items": collection.count(),
                "active": collection.name == self.collection_name,
            }
            for collection in sorted(
                self._get_client().list_collections(), key=lambda col: col.name
            )
        ]

    def list_sources(self) -> list[dict[str, object]]:
        connection = sqlite3.connect(f"{self.db_path.as_uri()}?mode=ro", uri=True)
        try:
            rows = connection.execute(
                "SELECT s.id, s.name, s.source_type, s.trust_level, "
                "COUNT(d.id), COALESCE(SUM(d.chunk_count), 0) "
                "FROM kbsource s LEFT JOIN kbdocument d ON d.source_id = s.id "
                "GROUP BY s.id ORDER BY s.name"
            ).fetchall()
        finally:
            connection.close()
        return [
            {
                "id": row[0],
                "name": row[1],
                "source_type": row[2],
                "trust_level": row[3],
                "documents": row[4],
                "chunks": row[5],
            }
            for row in rows
        ]

    def grounded_answer(self, query: str, citations: list[Citation]) -> str:
        if not citations:
            return "Insufficient KB context"
        primary = citations[0]
        command_lines = [
            line.strip("- ")
            for line in primary.text.splitlines()
            if line.strip().startswith(("- `", "`"))
        ][:3]
        actions = "\n".join(f"- {line}" for line in command_lines)
        return f"KB guidance from {primary.title}:\n{actions or primary.text[:500]}"
