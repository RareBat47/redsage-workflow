import json

from KB.workflow_build import build_preview_manifest


def test_build_preview_manifest_writes_sources_and_chunks(tmp_path):
    resources = tmp_path / "resources"
    source = resources / "09_scope_authorization" / "policy.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Scope\n\nAuthorization first.\n\nEvidence later.", encoding="utf-8")
    out = tmp_path / "out" / "manifest.json"

    manifest = build_preview_manifest(resources, out, max_chars=80)

    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert manifest["source_count"] == 1
    assert data["chunk_count"] >= 1
    assert data["sources"][0]["path"].endswith("policy.md")
    assert data["chunks"][0]["content_hash"]
    assert data["chunks"][0]["source_type"] == "redsage_policy"
    assert data["chunks"][0]["environment_scope"] == "authorized_engagement"
    assert data["chunks"][0]["is_approved"] is True
    assert data["chunks"][0]["is_unsafe"] is False
    assert data["chunks"][0]["source_version_id"].startswith("version_")
    assert data["chunks"][0]["document_id"].startswith("document_")
