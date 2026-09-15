"""Workflow-generation corpus selection, chunking, and metadata helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re


@dataclass(frozen=True)
class TextChunk:
    source_path: str
    ordinal: int
    text: str
    content_hash: str


def source_id_for_path(path: str | Path) -> str:
    normalized = str(Path(path)).replace("\\", "/")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    stem = re.sub(r"[^a-z0-9]+", "_", Path(path).stem.lower()).strip("_")[:40]
    stem = stem or "source"
    return f"workflow_{stem}_{digest}"


def chunk_text(text: str, max_chars: int = 2200, overlap: int = 250, source_path: str = "") -> list[TextChunk]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not cleaned:
        return []
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be non-negative and smaller than max_chars")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start : start + max_chars].strip())
                start += max_chars - overlap
            continue
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) > max_chars and current:
            chunks.append(current.strip())
            tail = current[-overlap:].strip() if overlap else ""
            current = f"{tail}\n\n{paragraph}" if tail else paragraph
        else:
            current = candidate
    if current:
        chunks.append(current.strip())

    records: list[TextChunk] = []
    for ordinal, chunk in enumerate(chunks):
        records.append(
            TextChunk(
                source_path=source_path,
                ordinal=ordinal,
                text=chunk,
                content_hash=hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
            )
        )
    return records


def read_text_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")
