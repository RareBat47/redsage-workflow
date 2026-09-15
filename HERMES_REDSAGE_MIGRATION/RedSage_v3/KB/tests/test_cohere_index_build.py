from pathlib import Path

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
    index_profile = {"provider": "cohere", "model": "test", "dimensions": 2}

    def embed_documents(self, texts):
        return [[float(i), float(i + 1)] for i, _ in enumerate(texts)]


def test_build_cohere_index_upserts_manifest_chunks(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"manifest_type":"redsage_v3_workflow_kb_preview","collection_name":"workflow_test","chunks":['
        '{"chunk_id":"c1","source_id":"s1","path":"p.md","ordinal":0,"text":"alpha","content_hash":"a"}'
        ']}', encoding="utf-8"
    )
    client = FakeClient()
    result = build_cohere_index(manifest, client=client, embedder=FakeEmbedder(), collection_name="workflow_test")
    assert result["vector_count"] == 1
    assert client.metadata[0] == "workflow_test"
    assert client.collection.calls[0]["ids"] == ["c1"]
    assert client.collection.calls[0]["metadatas"][0]["metadata_schema_version"] == "workflow-metadata-v1"
    assert client.metadata[1]["policy_version"] == "workflow-v1"
