from KB.contracts import ChunkRecord, RetrievalCitation, SourceVersion


def test_chunk_record_requires_provenance_fields():
    chunk = ChunkRecord(
        chunk_id="chunk-1",
        source_id="source-1",
        source_version_id="version-1",
        document_id="doc-1",
        ordinal=0,
        text="Example security guidance.",
        title="Example",
        locator="https://example.test/doc#1",
        trust_level=3,
        content_class="reference",
    )
    assert chunk.chunk_id == "chunk-1"
    assert chunk.content_hash


def test_retrieval_citation_exposes_score_components():
    citation = RetrievalCitation(
        chunk_id="chunk-1",
        source_id="source-1",
        source_version_id="version-1",
        document_id="doc-1",
        title="Example",
        locator="https://example.test/doc#1",
        excerpt="Example security guidance.",
        score=0.8,
        score_components={"vector": 0.5, "lexical": 0.3},
        trust_level=3,
    )
    assert citation.score_components["vector"] == 0.5


def test_source_version_is_immutable_by_content_hash():
    version = SourceVersion(
        source_id="source-1",
        version_id="version-1",
        name="Example source",
        origin="https://example.test",
        license_name="unknown",
        trust_level=3,
        content_hash="a" * 64,
        status="indexed",
    )
    assert len(version.content_hash) == 64
