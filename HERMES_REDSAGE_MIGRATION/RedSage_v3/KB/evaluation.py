"""Small offline regression suite for internal workflow retrieval behavior."""
from __future__ import annotations
from pathlib import Path
import json

CASES_PATH = Path(__file__).resolve().parent / "evaluation" / "cases.json"

def load_cases() -> list[dict]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))

def evaluate_case_output(output: dict, expected: dict) -> dict:
    text = json.dumps(output, ensure_ascii=False).lower()
    missing = [term for term in expected.get("must_include", []) if term.lower() not in text]
    return {"passed": not missing, "missing": missing}
