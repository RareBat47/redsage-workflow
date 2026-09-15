from KB.cohere_index import build_cohere_index


class FakeCollection:
    def __init__(self):
        self.calls = []

    def upsert(self, **kwargs):
        self.calls.append(kwargs)


class FakeClient:
    def __init__(self):
        self.collection = FakeCollection()
        self.metadata = None

    def get_or_create_collection(self, name, metadata=None):
        self.metadata = (name, metadata)
        return self.collection


class FakeEmbedder:
    model = "test-model"
    index_profile = {"provider": "cohere", "model": "test-model", "dimensions": 2}

    def embed_documents(self, texts):
        return [[float(i), float(i + 1)] for i, _ in enumerate(texts)]


def test_reporting_manifest_uses_reporting_schema_and_preserves_class(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"manifest_type":"redsage_v3_reporting_kb_preview","collection_name":"reporting","chunks":['
        '{"chunk_id":"c1","source_id":"s1","path":"p.md","ordinal":0,"text":"alpha",'
        '"content_hash":"a","reporting_class":"evidence","source_type":"redsage_domain",'
        '"environment_scope":"authorized_engagement","is_approved":true,"is_unsafe":false,'
        '"trust_level":5,"source_version_id":"v1","document_id":"d1","title":"Guide",'
        '"locator":"p.md#1","content_class":"evidence_guidance","policy_tags":"[]",'
        '"reporting_metadata_schema_version":"reporting-v1"}'
        ']}'
    )
    client = FakeClient()
    result = build_cohere_index(manifest, client=client, embedder=FakeEmbedder(), collection_name="reporting")
    assert result["vector_count"] == 1
    assert client.metadata[1]["metadata_schema_version"] == "reporting-v1"
    assert client.metadata[1]["policy_version"] == "reporting-v1"
    assert client.collection.calls[0]["metadatas"][0]["reporting_class"] == "evidence"
