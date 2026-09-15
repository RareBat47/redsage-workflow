from KB.cohere_embeddings import CohereEmbeddingAdapter, extract_float_embeddings


def test_extract_float_embeddings_supports_cohere_v5_response_shape():
    response = type("Response", (), {})()
    response.embeddings = type("Embeddings", (), {"float_": [[0.1, 0.2], [0.3, 0.4]]})()
    assert extract_float_embeddings(response) == [[0.1, 0.2], [0.3, 0.4]]


def test_adapter_records_explicit_index_profile():
    adapter = CohereEmbeddingAdapter.__new__(CohereEmbeddingAdapter)
    adapter.model = "embed-english-v3.0"
    adapter.dimensions = 1024
    assert adapter.index_profile == {
        "provider": "cohere",
        "model": "embed-english-v3.0",
        "document_input_type": "search_document",
        "query_input_type": "search_query",
        "dimensions": 1024,
    }
