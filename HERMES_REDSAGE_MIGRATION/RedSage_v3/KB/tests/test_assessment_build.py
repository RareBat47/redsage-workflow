import json

from KB.assessment_build import build_assessment_preview


def test_assessment_preview_assigns_specific_phases(tmp_path):
    root = tmp_path / "resources"
    paths = {
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/01-test.md": "authorization idor access control",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/04-Authentication/01-test.md": "authentication login session",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/07-Injection/01-test.md": "input validation injection",
    }
    for relative, content in paths.items():
        path = root / relative
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")
    output = tmp_path / "manifest.json"

    result = build_assessment_preview(root, output, max_chars=100)
    phases = {chunk["assessment_phase"] for chunk in result["chunks"]}

    assert "authorization" in phases
    assert "identity_session" in phases
    assert "input_validation" in phases
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["embedding_status"] == "not_embedded"
