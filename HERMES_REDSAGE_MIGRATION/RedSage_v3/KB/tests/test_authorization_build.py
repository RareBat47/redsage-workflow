from KB.authorization_build import select_authorization_sources, build_authorization_preview


def test_authorization_selector_includes_access_control_and_business_logic(tmp_path):
    root = tmp_path / "resources"
    files = {
        "03_owasp/cheatsheet_series/cheatsheets/Authorization_Cheat_Sheet.md": "access control",
        "03_owasp/cheatsheet_series/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.md": "idor",
        "03_owasp/cheatsheet_series/cheatsheets/Business_Logic_Security_Cheat_Sheet.md": "business logic",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md": "authorization",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/10-Business_Logic/test.md": "workflow",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/04-Authentication/test.md": "login",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    names = {path.relative_to(root).as_posix() for path in select_authorization_sources(root)}
    assert "03_owasp/cheatsheet_series/cheatsheets/Authorization_Cheat_Sheet.md" in names
    assert "03_owasp/cheatsheet_series/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.md" in names
    assert "03_owasp/cheatsheet_series/cheatsheets/Business_Logic_Security_Cheat_Sheet.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/10-Business_Logic/test.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/04-Authentication/test.md" not in names


def test_authorization_preview_is_unembedded_and_classified(tmp_path):
    root = tmp_path / "resources"
    path = root / "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md"
    path.parent.mkdir(parents=True)
    path.write_text("authorization and object access", encoding="utf-8")
    result = build_authorization_preview(root, tmp_path / "manifest.json")
    assert result["embedding_status"] == "not_embedded"
    assert result["chunks"][0]["authorization_class"] in {"access_control", "object_access"}
