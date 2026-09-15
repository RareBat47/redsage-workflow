from KB.identity_retrieval_service import search_identity_kb


class Embedder:
    def embed_query(self, query):
        return [0.1, 0.2]


class Collection:
    def query(self, **kwargs):
        return {
            "ids": [["auth", "session", "unsafe"]],
            "documents": [["authentication login evidence", "session cookie evidence", "unsafe" ]],
            "metadatas": [[
                {"path": "03_owasp/auth.md", "source_id": "a", "source_version_id": "v1", "document_id": "d1", "title": "Auth", "locator": "auth.md", "source_type": "owasp", "content_class": "assessment_objective", "environment_scope": "authorized_engagement", "is_approved": True, "is_unsafe": False, "trust_level": 4, "identity_class": "authentication", "content_hash": "a" * 64},
                {"path": "03_owasp/session.md", "source_id": "s", "source_version_id": "v1", "document_id": "d2", "title": "Session", "locator": "session.md", "source_type": "owasp", "content_class": "assessment_objective", "environment_scope": "authorized_engagement", "is_approved": True, "is_unsafe": False, "trust_level": 4, "identity_class": "session_management", "content_hash": "b" * 64},
                {"path": "03_owasp/unsafe.md", "source_id": "u", "source_version_id": "v1", "document_id": "d3", "title": "Unsafe", "locator": "unsafe.md", "source_type": "owasp", "content_class": "unsafe", "environment_scope": "authorized_engagement", "is_approved": True, "is_unsafe": True, "trust_level": 4, "identity_class": "authentication", "content_hash": "c" * 64},
            ]],
            "distances": [[0.1, 0.2, 0.05]],
        }


class Client:
    def get_collection(self, name):
        return Collection()


def test_identity_retrieval_returns_identity_metadata_and_filters_unsafe(tmp_path):
    result = search_identity_kb("authorized authentication and session assessment", client=Client(), embedder=Embedder(), receipt_directory=tmp_path)
    assert len(result["citations"]) == 2
    assert all(item["identity_class"] for item in result["citations"])
    assert result["filtered_count"] == 1
    assert (tmp_path / f"{result['query_id']}.json").exists()
