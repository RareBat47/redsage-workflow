#!/usr/bin/env python3
"""Verify the public release bundle is safe to publish.

Fails (exit 1) when:
  1. A forbidden file or directory exists anywhere in the bundle.
  2. A scanned text file contains a secret-like value (best-effort scan).

Usage:
    python scripts/verify_public_bundle.py [--root DIR] [--report-only]

`--root` defaults to the parent of the `scripts/` directory (the bundle root).

Notes on the scanner:
  - It looks for *assigned values* (e.g. `CO_API_KEY=...`, `password = "..."`,
    `Bearer <token>`, PEM private-key blocks, 40+ char quoted tokens), not for
    bare mentions of keyword names. Documentation that says "set CO_API_KEY"
    is therefore fine.
  - Known synthetic fixtures used by the redaction tests are allowlisted below
    and still printed so a human can audit them. package-lock.json integrity
    hashes (npm `sha512-...` digests) are not secrets and are skipped.
  - The scanner never reads its own source (it must contain the patterns).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Forbidden paths (hard fail if present)
# ---------------------------------------------------------------------------
FORBIDDEN_PATHS: set[str] = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
    "data/redsage.db",
    "data/verify_all.db",
    "data/projects",
    "data/chroma",
    "frontend/node_modules",
    "frontend/dist",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "tests/e2e/__pycache__",
    "tests/__pycache__",
    "backend/__pycache__",
    "backend/services/__pycache__",
    "backend/routers/__pycache__",
    "backend/models/__pycache__",
    "backend/schemas/__pycache__",
}

FORBIDDEN_SUFFIXES: set[str] = {".pyc", ".pyo"}

FORBIDDEN_NAMES: set[str] = {"__pycache__"}

# ---------------------------------------------------------------------------
# 2. Secret-like pattern scan
# ---------------------------------------------------------------------------
TEXT_EXTENSIONS: set[str] = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml", ".ini", ".cfg", ".toml",
    ".sh", ".ps1", ".ts", ".tsx", ".js", ".jsx", ".css", ".html",
}

# Values that are obviously placeholders / documentation, never secrets.
_PLACEHOLDER_VALUES: set[str] = {
    "", "your-key-here", "replace-with-your-key", "replace-with-", "replace-me",
    "changeme", "change-me", "example", "xxxxx", "xxx", "xxxx", "todo", "none",
    "unset", "blank", "false", "true", "null", "nan", "<key>", "<your-key>",
    "<api-key>", "<token>", "<password>", "<secret>", "..." ,
}
# Values that are clearly code expressions rather than literal secrets.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_EXPRESSION_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*\(.*\)$")


def _looks_like_value(raw: str) -> bool:
    value = raw.strip().strip("\"'`")
    if "`" in value or "{" in value:
        return False  # markdown documentation or f-string fragment
    if value.endswith(")"):
        value = value[:-1]  # expression fragment such as "api_key)"
    if value.lower() in _PLACEHOLDER_VALUES:
        return False
    if _IDENTIFIER_RE.match(value) or _EXPRESSION_RE.match(value):
        return False
    if value.lower().startswith(("os.getenv", "settings.", "config.", "env[")):
        return False
    return len(value) >= 4


_ENV_KEY_RE = re.compile(
    r"^[ \t]*(?:CO_API_KEY|COHERE_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|"
    r"GEMINI_API_KEY|AZURE_OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|"
    r"MYSQL_PASSWORD|POSTGRES_PASSWORD|REDIS_PASSWORD|SECRET_KEY|JWT_SECRET|"
    r"API_KEY|TOKEN)\s*=\s*(.+?)[ \t]*$",
    re.IGNORECASE,
)

_KEYWORD_ASSIGN_RE = re.compile(
    r"\b(?:api[_-]?key|apikey|secret|access[_-]?token|auth[_-]?token|"
    r"refresh[_-]?token|private[_-]?key|password|passwd)\b\s*[:=]\s*"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
    re.IGNORECASE,
)

_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/=]{20,}")

_PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----")

_CONNECTION_STRING_RE = re.compile(
    r"(?i)(?:postgres|postgresql|mysql|mongodb|redis|amqp|mssql)://"
    r"[^\s/:]+:[^\s@/]+@"
)

_LONG_TOKEN_RE = re.compile(r"[\"'][A-Za-z0-9_\-./+=]{40,}[\"']")

_UPPERCASE_SECRET_ASSIGN_RE = re.compile(
    r"^[ \t]*[A-Z][A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API[_-]?KEY|"
    r"CREDENTIAL)[A-Z0-9_]*\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
)

_INTEGRITY_LINE_RE = re.compile(r"^\s*\"integrity\"\s*:\s*\"sha")

_PATTERNS: list[tuple[str, "re.Pattern[str]"]] = [
    ("env assignment", _ENV_KEY_RE),
    ("keyword assignment", _KEYWORD_ASSIGN_RE),
    ("uppercase secret assignment", _UPPERCASE_SECRET_ASSIGN_RE),
    ("bearer token", _BEARER_RE),
    ("private key block", _PRIVATE_KEY_RE),
    ("connection string with credentials", _CONNECTION_STRING_RE),
    ("long token", _LONG_TOKEN_RE),
]


def _clean_value(match: re.Match[str], pattern_name: str) -> str:
    """Extract the value portion from a match for reporting."""
    try:
        return match.group(1)
    except IndexError:
        if pattern_name == "keyword assignment":
            text = match.group(0)
            return text.split("=", 1)[-1].split(":", 1)[-1].strip().strip("\"'")
        if pattern_name == "bearer token":
            return match.group(0)[len("Bearer "):]
        return match.group(0)


def scan_text(path: Path) -> list[str]:
    """Return human-readable findings for one text file."""
    findings: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as error:
        findings.append(f"  [unreadable] {path}: {error}")
        return findings
    for line_no, line in enumerate(lines, start=1):
        if _INTEGRITY_LINE_RE.match(line):
            continue  # npm package-lock sha512 digests, not secrets
        for name, pattern in _PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            value = _clean_value(match, name)
            if not _looks_like_value(value):
                continue
            if name == "long token" and ("/" in value or "\\" in value):
                continue  # path-like strings, not credentials
            findings.append(f"  {path}:{line_no} [{name}]: {value[:60]!r}")
    return findings


# Known synthetic fixtures used by the redaction / export integrity tests.
# These are fake values whose entire purpose is to prove secrets are stripped;
# they must remain so the tests stay meaningful. Reviewed 2026-09-08.
ALLOWLISTED_FIXTURES: dict[str, str] = {
    "tests/test_release_hardening.py": (
        "synthetic password/bearer/JWT fixtures used to prove redaction and "
        "export integrity; values are fabricated test constants"
    ),
    "tests/test_sanitizer.py": (
        "synthetic encoded-secret fixtures used to prove CLI/encoded redaction"
    ),
    "tests/test_artifacts.py": (
        "synthetic password string used to prove artifacts store only "
        "redacted excerpts"
    ),
    "tests/test_live_ai_benchmark.py": (
        "synthetic bearer/password fixtures used to prove pre-dispatch "
        "redaction in the optional live benchmark"
    ),
    "tests/test_smoke_demo.py": (
        "synthetic fake JWT used to prove bearer/JWT redaction in the smoke test"
    ),
}


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--report-only", action="store_true",
                        help="print findings but never fail")
    args = parser.parse_args()

    root = args.root.resolve()
    problems: list[str] = []
    allowlisted: list[str] = []
    scanned_files = 0

    print(f"Verifying public bundle: {root}")

    # -- forbidden files/directories --------------------------------------
    print("\n[1/2] Forbidden files and directories")
    for path in sorted(root.rglob("*")):
        rel = relative(path, root)
        if rel.startswith(".git/"):
            continue
        hit = (
            rel in FORBIDDEN_PATHS
            or path.name in FORBIDDEN_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
        )
        if hit:
            problems.append(f"FORBIDDEN: {rel}")
            print(f"  FAIL  {rel}")
    if not any(str(p).startswith("FORBIDDEN") for p in problems):
        print("  OK    no forbidden files or directories found")

    # -- secret-like content scan -----------------------------------------
    print("\n[2/2] Secret-like content scan")
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = relative(path, root)
        if rel.startswith(".git/"):
            continue
        if rel == "scripts/verify_public_bundle.py":
            continue  # scanner itself; it must contain the patterns
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        scanned_files += 1
        findings = scan_text(path)
        for finding in findings:
            if rel in ALLOWLISTED_FIXTURES:
                allowlisted.append(finding)
                continue
            problems.append(f"SECRET-LIKE: {finding.strip()}")
    if problems:
        for problem in problems:
            print(f"  FAIL  {problem}")
    else:
        print(f"  OK    {scanned_files} text files scanned, no secret-like values")

    if allowlisted:
        print("\nAllowlisted synthetic test fixtures (reviewed, not secrets):")
        for entry in allowlisted:
            print(f"  INFO  {entry.strip()}")

    print(f"\nResult: {'FAIL' if problems else 'PASS'} "
          f"({len(problems)} problem(s), {scanned_files} files scanned)")
    if problems and not args.report_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
