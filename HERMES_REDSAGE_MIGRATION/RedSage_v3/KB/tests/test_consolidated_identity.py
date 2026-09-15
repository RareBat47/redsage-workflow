from KB.consolidated_retrieval import KBProfile, search_consolidated


def test_duplicate_chunk_ids_are_namespaced_by_kb_domain(tmp_path):
    class Collection:
        def query(self, **kwargs):
            return {
                "ids": [["same"]],
                "documents": [["guidance"]],
                "metadatas": [[{
                    "path": "03_owasp/item.md", "source_id": "s", "source_version_id": "v",
                    "document_id": "d", "title": "Item", "locator": "item.md",
                    "content_hash": "a" * 64, "source_type": "owasp",
                    "content_class": "reference", "environment_scope": "authorized_engagement",
                    "is_approved": True, "is_unsafe": False, "trust_level": 4,
                }]],
                "distances": [[0.1]],
            }

    class Client:
        def get_collection(self, name):
            return Collection()

    class Embedder:
        def embed_query(self, query):
            return [0.1]

    result = search_consolidated(
        "authorized guidance",
        profiles=[KBProfile("one", "web", "v1"), KBProfile("two", "api", "v1")],
        client=Client(), embedder=Embedder(), receipt_directory=tmp_path,
    )
    assert len(result["citations"]) == 2
    assert len({item["citation_key"] for item in result["citations"]}) == 2
    assert {item["chunk_id"] for item in result["citations"]} == {"same"}
