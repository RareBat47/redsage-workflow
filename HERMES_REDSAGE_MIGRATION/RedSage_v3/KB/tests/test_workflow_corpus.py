from KB.workflow_corpus import chunk_text, source_id_for_path


def test_chunk_text_preserves_heading_and_limits_size():
    text = "# Scope\n" + "A" * 120 + "\n\n## Evidence\n" + "B" * 120
    chunks = chunk_text(text, max_chars=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk.text) <= 140 for chunk in chunks)
    assert chunks[0].ordinal == 0
    assert chunks[0].content_hash


def test_source_id_for_path_is_stable_and_readable():
    first = source_id_for_path("RESOURCES/WORKFLOW_GENERATION/03_owasp/top10_README.md")
    second = source_id_for_path("RESOURCES/WORKFLOW_GENERATION/03_owasp/top10_README.md")
    assert first == second
    assert first.startswith("workflow_")
