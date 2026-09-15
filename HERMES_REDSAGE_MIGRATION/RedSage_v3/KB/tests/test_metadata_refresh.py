from KB.metadata_refresh import refresh_collection_metadata


class Collection:
    def __init__(self):
        self.calls = []

    def update(self, **kwargs):
        self.calls.append(kwargs)


class Client:
    def __init__(self):
        self.collection = Collection()

    def get_collection(self, name):
        return self.collection


def test_refresh_collection_metadata_updates_existing_vectors_from_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"manifest_type":"redsage_v3_workflow_kb_preview","chunks":['
        '{"chunk_id":"c1","source_type":"owasp","environment_scope":"authorized_engagement",'
        '"is_approved":true,"is_unsafe":false,"trust_level":4,"content_hash":"a"}'
        ']}'
    )
    client = Client()
    result = refresh_collection_metadata(manifest, client=client, collection_name="workflow")
    assert result["updated_count"] == 1
    assert client.collection.calls[0]["ids"] == ["c1"]
    assert client.collection.calls[0]["metadatas"][0]["source_type"] == "owasp"
