from KB.identity_build import select_identity_sources


def test_identity_selector_includes_identity_sources_and_excludes_unrelated(tmp_path):
    root = tmp_path / "resources"
    files = {
        "03_owasp/cheatsheet_series/cheatsheets/Authentication_Cheat_Sheet.md": "authentication login",
        "03_owasp/cheatsheet_series/cheatsheets/Session_Management_Cheat_Sheet.md": "session cookie",
        "03_owasp/cheatsheet_series/cheatsheets/OAuth2_Cheat_Sheet.md": "oauth token",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/test.md": "session",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md": "access control",
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    names = {path.relative_to(root).as_posix() for path in select_identity_sources(root)}
    assert "03_owasp/cheatsheet_series/cheatsheets/Authentication_Cheat_Sheet.md" in names
    assert "03_owasp/cheatsheet_series/cheatsheets/Session_Management_Cheat_Sheet.md" in names
    assert "03_owasp/cheatsheet_series/cheatsheets/OAuth2_Cheat_Sheet.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/test.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md" not in names
