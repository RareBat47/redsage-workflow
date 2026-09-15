from KB.lab_build import build_lab_preview


def test_lab_preview_marks_lab_only_and_separate_collection(tmp_path):
    root = tmp_path / "resources" / "08_lab_ctf"
    root.mkdir(parents=True)
    (root / "writeup.md").write_text("controlled lab reasoning", encoding="utf-8")
    result = build_lab_preview(tmp_path / "resources", tmp_path / "manifest.json")
    assert result["collection_name"] == "redsage_v3_lab_cohere_v1"
    assert result["chunks"][0]["environment_scope"] == "lab_only"
    assert result["chunks"][0]["source_type"] == "lab"
    assert result["embedding_status"] == "not_embedded"
