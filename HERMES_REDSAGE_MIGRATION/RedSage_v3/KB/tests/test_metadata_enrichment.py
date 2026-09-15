from pathlib import Path

from KB.workflow_build import enrich_source_metadata


def test_enrich_source_metadata_assigns_explicit_policy_metadata():
    metadata = enrich_source_metadata(Path("03_owasp/wstg/document/test.md"), "abc" * 10)
    assert metadata["source_type"] == "owasp"
    assert metadata["environment_scope"] == "authorized_engagement"
    assert metadata["is_approved"] is True
    assert metadata["is_unsafe"] is False
    assert metadata["trust_level"] == 4
    assert metadata["source_version_id"].startswith("version_")
    assert metadata["document_id"].startswith("document_")


def test_enrich_unknown_source_fails_closed():
    metadata = enrich_source_metadata(Path("unknown/file.md"), "abc" * 10)
    assert metadata["source_type"] == "unknown"
    assert metadata["environment_scope"] == "unknown"
    assert metadata["is_approved"] is False
    assert metadata["is_unsafe"] is True
