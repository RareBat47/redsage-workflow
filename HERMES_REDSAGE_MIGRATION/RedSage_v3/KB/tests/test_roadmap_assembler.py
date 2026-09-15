from KB.roadmap_assembler import assemble_roadmap


def test_assembler_creates_gated_web_roadmap_from_retrieval():
    result = assemble_roadmap(
        "Authorized web app assessment of login and object access",
        retrieval={
            "query_id": "q1",
            "query_classification": {"primary": "authentication"},
            "citations": [{"citation": "[1] Auth Guide", "locator": "auth.md"}],
            "warnings": [],
        },
    )
    assert result["status"] == "READY_FOR_REVIEW"
    assert result["target_type"] == "web_app"
    assert len(result["phases"]) == 7
    assert all(phase["tasks"] for phase in result["phases"])
    assert result["receipt_id"] == "q1"


def test_assembler_blocks_missing_authorization():
    result = assemble_roadmap(
        "Test this website for bugs",
        retrieval={
            "query_id": "q2",
            "query_classification": {"primary": "general_workflow"},
            "citations": [],
            "warnings": [],
        },
    )
    assert result["status"] == "NEEDS_CLARIFICATION"
    assert result["safety"]["decision"] == "BLOCKED"
    assert result["clarification_questions"]
    assert not result["phases"]


def test_assembler_marks_lab_context():
    result = assemble_roadmap(
        "Authorized training lab web application",
        retrieval={
            "query_id": "q3",
            "query_classification": {"primary": "lab"},
            "citations": [],
            "warnings": [],
        },
        environment_scope="lab_only",
    )
    assert result["environment_scope"] == "lab_only"
    assert result["safety"]["decision"] == "LAB_ONLY"
