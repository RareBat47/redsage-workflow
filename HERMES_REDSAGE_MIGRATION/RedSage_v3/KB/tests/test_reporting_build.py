from KB.reporting_build import build_reporting_preview


def test_reporting_preview_selects_reporting_sources(tmp_path):
    root = tmp_path / "resources"
    files = {
        "02_redsage_domain/v2_verified/SECURITY.md": "evidence reporting findings remediation",
        "03_owasp/cheatsheet_series/cheatsheets/Logging_Cheat_Sheet.md": "logging evidence",
        "04_cwe_cvss/CVSS_V4_SPECIFICATION.html": "severity scoring",
        "03_owasp/wstg/document/report.md": "report findings evidence",
        "03_owasp/wstg/document/05-Authorization.md": "authorization only",
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    result = build_reporting_preview(root, tmp_path / "manifest.json")

    paths = {chunk["path"] for chunk in result["chunks"]}
    assert "02_redsage_domain/v2_verified/SECURITY.md" in paths
    assert "04_cwe_cvss/CVSS_V4_SPECIFICATION.html" in paths
    assert "03_owasp/wstg/document/05-Authorization.md" not in paths
    assert result["embedding_status"] == "not_embedded"
    assert all(chunk["reporting_class"] for chunk in result["chunks"])
