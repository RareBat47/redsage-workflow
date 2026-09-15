"""Stable, provider-neutral contracts for the RedSage v3 knowledge base."""

from dataclasses import dataclass, field
import hashlib


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    source_id: str
    source_version_id: str
    document_id: str
    ordinal: int
    text: str
    title: str
    locator: str
    trust_level: int
    content_class: str
    content_hash: str = ""

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("chunk text must not be empty")
        if not self.content_hash:
            object.__setattr__(
                self,
                "content_hash",
                hashlib.sha256(self.text.encode("utf-8")).hexdigest(),
            )
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 hex digest")
        if not 0 <= self.trust_level <= 5:
            raise ValueError("trust_level must be between 0 and 5")


@dataclass(frozen=True)
class SourceVersion:
    source_id: str
    version_id: str
    name: str
    origin: str
    license_name: str
    trust_level: int
    content_hash: str
    status: str

    def __post_init__(self) -> None:
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 hex digest")


@dataclass(frozen=True)
class RetrievalCitation:
    chunk_id: str
    source_id: str
    source_version_id: str
    document_id: str
    title: str
    locator: str
    excerpt: str
    score: float
    score_components: dict[str, float] = field(default_factory=dict)
    trust_level: int = 0


@dataclass(frozen=True)
class RetrievalResult:
    query_id: str
    index_profile: str
    policy_version: str
    citations: tuple[RetrievalCitation, ...]
    warnings: tuple[str, ...] = ()
    retrieval_timestamp: str = ""
