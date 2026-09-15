"""Hybrid ranking and lightweight classification for workflow retrieval."""

from __future__ import annotations

import re
import string
from typing import Any

_STOPWORDS = frozenset(
    "a an and are as at be but by do for how i in is it of on or the to what "
    "when where which who why with you your".split()
)

_QUERY_CLASSES = {
    "authorization_scope": ("authorization", "authorized", "scope", "permission", "out of scope", "exclusion", "rate limit", "safe harbor"),
    "lab": ("ctf", "capture the flag", "training lab", "lab environment", "deliberately vulnerable"),
    "api": ("api", "rest", "graphql", "websocket", "grpc"),
    "authentication": ("login", "authentication", "session", "cookie", "oauth", "jwt"),
    "authorization_testing": ("idor", "bola", "access control", "privilege"),
    "evidence_reporting": ("evidence", "report", "finding", "remediation", "severity"),
}


def _tokens(text: str) -> set[str]:
    return {
        word.strip(string.punctuation).lower()
        for word in text.split()
        if word.strip(string.punctuation)
    }


def classify_query(query: str) -> dict[str, Any]:
    lowered = query.lower()
    matches = {
        name: sum(1 for term in terms if term in lowered)
        for name, terms in _QUERY_CLASSES.items()
    }
    # Scope ambiguity is a hard gate and therefore wins ties and technical matches.
    if matches["authorization_scope"]:
        primary = "authorization_scope"
    else:
        primary = max(matches, key=matches.get)
        if matches[primary] == 0:
            primary = "general_workflow"
    return {"primary": primary, "matches": matches}


def rank_chunks(query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_tokens = _tokens(query) - _STOPWORDS
    classification = classify_query(query)
    ranked: list[dict[str, Any]] = []
    for original in candidates:
        item = dict(original)
        lexical = len(query_tokens & _tokens(str(item.get("text", "")))) / max(1, len(query_tokens))
        vector = float(item.get("vector_score", 0.0))
        trust = 0.05 * max(0, min(int(item.get("trust_level", 0)), 5))
        policy = 0.0
        if classification["primary"] == "authorization_scope" and item.get("source_type") == "redsage_policy":
            policy = 1.0
        elif classification["primary"] == "lab" and item.get("source_type") == "lab":
            policy = 0.5
        elif classification["primary"] != "lab" and item.get("source_type") == "lab":
            policy = -0.25
        lab_penalty = 0.25 if item.get("environment_scope") == "lab_only" and classification["primary"] != "lab" else 0.0
        score = vector + lexical + trust + policy - lab_penalty
        item["score"] = score
        item["score_components"] = {"vector": vector, "lexical": lexical, "trust": trust, "policy": policy, "lab_penalty": lab_penalty}
        ranked.append(item)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)
