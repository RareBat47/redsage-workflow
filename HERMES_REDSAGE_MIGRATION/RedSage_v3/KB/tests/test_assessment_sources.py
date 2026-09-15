from KB.assessment_sources import select_assessment_sources


def test_assessment_selection_includes_web_guidance_and_policies(tmp_path):
    root = tmp_path / "resources"
    for relative in (
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md",
        "03_owasp/selected_cheatsheet_Authorization_Cheat_Sheet.md",
        "04_cwe_cvss/CVSS_V4_SPECIFICATION.html",
        "09_scope_authorization/policy.md",
        "10_stop_escalation/stops.md",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("assessment guidance", encoding="utf-8")

    selected = select_assessment_sources(root)
    names = {path.relative_to(root).as_posix() for path in selected}
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md" in names
    assert "09_scope_authorization/policy.md" in names
    assert "10_stop_escalation/stops.md" in names


def test_assessment_selection_excludes_planning_only_and_lab_content(tmp_path):
    root = tmp_path / "resources"
    for relative in (
        "01_methodology_book/BOOK_CANDIDATES.txt",
        "08_lab_ctf/lab.md",
        "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/test.md",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("content", encoding="utf-8")

    names = {path.relative_to(root).as_posix() for path in select_assessment_sources(root)}
    assert "03_owasp/wstg/document/4-Web_Application_Security_Testing/06-Session_Management/test.md" in names
    assert "01_methodology_book/BOOK_CANDIDATES.txt" not in names
    assert "08_lab_ctf/lab.md" not in names
