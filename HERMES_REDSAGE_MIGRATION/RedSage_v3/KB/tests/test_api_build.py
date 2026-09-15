from KB.api_build import build_api_preview, select_api_sources


def test_api_selector_includes_api_guidance_and_excludes_unrelated_identity_content(tmp_path):
    root = tmp_path / "resources"
    files = {
        "03_owasp/cheatsheet_series/cheatsheets/REST_Security_Cheat_Sheet.md": "REST API authentication rate limiting",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/02-API_Broken_Object_Level_Authorization.md": "BOLA API",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/03-API_Broken_Object_Property_Level_Authorization.md": "object property authorization",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/04-API_Improper_Inventory_Management.md": "API inventory",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/01-Session_Management_Schema.md": "session cookie",
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    names = {path.relative_to(root).as_posix() for path in select_api_sources(root)}
    assert "03_owasp/cheatsheet_series/cheatsheets/REST_Security_Cheat_Sheet.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/02-API_Broken_Object_Level_Authorization.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/03-API_Broken_Object_Property_Level_Authorization.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/04-API_Improper_Inventory_Management.md" in names
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/01-Session_Management_Schema.md" not in names


def test_api_preview_is_unembedded_and_has_api_metadata(tmp_path):
    root = tmp_path / "resources"
    path = root / "03_owasp/wstg/document/4-Web_Application_Security_Testing/12-API_Testing/test.md"
    path.parent.mkdir(parents=True)
    path.write_text("API schema validation and rate limit", encoding="utf-8")
    result = build_api_preview(root, tmp_path / "manifest.json")
    assert result["embedding_status"] == "not_embedded"
    assert result["chunks"][0]["api_class"] in {"schema_validation", "rate_limit", "api_general"}
