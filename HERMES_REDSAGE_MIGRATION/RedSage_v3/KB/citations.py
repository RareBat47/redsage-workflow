"""Human-readable, provenance-preserving citation assembly."""
from __future__ import annotations
from typing import Any


def assemble_citations(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in items:
        title = str(item.get("title") or item.get("path") or "Untitled source")
        source_type = str(item.get("source_type") or "unknown")
        trust = int(item.get("trust_level", 0))
        approved = item.get("is_approved", False)
        notice = None if approved else "Source is not approved for publication; use for internal review only."
        result.append({
            **item,
            "citation": f"{item.get('citation_id', '')} {title} — {source_type}, trust {trust}".strip(),
            "title": title,
            "source_type": source_type,
            "trust_level": trust,
            "locator": str(item.get("locator") or item.get("path") or ""),
            "excerpt": str(item.get("excerpt") or ""),
            "notice": notice,
        })
    return result


def render_citations(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in assemble_citations(items):
        lines.append(item["citation"])
        lines.append(f"  Location: {item['locator']}")
        if item["notice"]:
            lines.append(f"  Notice: {item['notice']}")
        lines.append(f"  Excerpt: {item['excerpt']}")
    return "\n".join(lines)
