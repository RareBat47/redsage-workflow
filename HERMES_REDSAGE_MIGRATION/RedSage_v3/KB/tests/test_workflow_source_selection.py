from pathlib import Path

from KB.workflow_sources import select_workflow_sources


def test_select_workflow_sources_includes_text_files_and_excludes_archives(tmp_path):
    root = tmp_path / "resources"
    (root / "03_owasp").mkdir(parents=True)
    good = root / "03_owasp" / "guide.md"
    good.write_text("# Guide\nworkflow", encoding="utf-8")
    archive = root / "03_owasp" / "raw.zip"
    archive.write_bytes(b"zip")
    image = root / "03_owasp" / "diagram.png"
    image.write_bytes(b"png")

    selected = select_workflow_sources(root)

    assert good in selected
    assert archive not in selected
    assert image not in selected


def test_select_workflow_sources_excludes_git_and_node_artifacts(tmp_path):
    root = tmp_path / "resources"
    git_file = root / "03_owasp" / ".git" / "config"
    node_file = root / "03_owasp" / "node_modules" / "x.md"
    keep = root / "09_scope_authorization" / "policy.md"
    git_file.parent.mkdir(parents=True)
    node_file.parent.mkdir(parents=True)
    keep.parent.mkdir(parents=True)
    git_file.write_text("git", encoding="utf-8")
    node_file.write_text("node", encoding="utf-8")
    keep.write_text("policy", encoding="utf-8")

    selected = select_workflow_sources(root)

    assert keep in selected
    assert git_file not in selected
    assert node_file not in selected
