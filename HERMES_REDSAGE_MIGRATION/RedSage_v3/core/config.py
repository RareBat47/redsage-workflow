"""Central configuration: paths, embedding model, and retrieval defaults.

All values can be overridden with environment variables (or a .env file).
Defaults match the preserved Knowledge Base exactly so the existing
ChromaDB vectors remain queryable without any migration.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    chroma_dir: Path
    sqlite_db: Path
    embedding_provider: str
    active_collection: str
    cohere_embed_model: str
    top_k: int
    score_threshold: float
    distance_metric: str


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


settings = Settings(
    chroma_dir=Path(os.getenv("REDSAGE_CHROMA_DIR", str(PROJECT_ROOT / "data" / "chroma"))),
    sqlite_db=Path(os.getenv("REDSAGE_DB", str(PROJECT_ROOT / "data" / "redsage.db"))),
    embedding_provider=os.getenv("REDSAGE_EMBEDDING_PROVIDER", "local"),
    active_collection=os.getenv("REDSAGE_COLLECTION", "redsage_kb_local_v4"),
    cohere_embed_model=os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0"),
    top_k=_int_env("REDSAGE_TOP_K", 5),
    score_threshold=_float_env("REDSAGE_SCORE_THRESHOLD", 0.15),
    distance_metric=os.getenv("REDSAGE_DISTANCE_METRIC", "l2"),
)
