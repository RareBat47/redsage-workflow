from KB.assessment_retrieval_service import search_assessment_kb


class Embedder:
    def embed_query(self, query):
        return [0.1, 0.2]


class Collection:
    def query(self, **kwargs):
        return {
            "ids": [["auth", "general", "lab"]],
            "documents": [[
                "object level authorization evidence",
                "general assessment guidance",
                "lab-only authorization example",
            ]],
            "metadatas": [[
                {
                    "path": "03_owasp/wstg/document/4-Web_Application_Security_Testing/05-Authorization/test.md",
                    "source_id": "s1", "source_version_id": "v1", "document_id": "d1",
                    "title": "Authorization Test", "locator": "test.md#1",
                    "source_type": "owasp", "content_class": "assessment_objective",
                    "environment_scope": "authorized_engagement", "is_approved": True,
                    "is_unsafe": False, "trust_level": 4, "assessment_phase": "authorization",
                    "content_hash": "a" * 64,
                },
                {
                    "path": "03_owasp/wstg/general.md", "source_id": "s2",
                    "source_version_id": "v1", "document_id": "d2", "title": "General",
                    "locator": "general.md#1", "source_type": "owasp",
                    "content_class": "reference", "environment_scope": "authorized_engagement",
                    "is_approved": True, "is_unsafe": False, "trust_level": 4,
                    "assessment_phase": "assessment_general", "content_hash": "b" * 64,
                },
                {
                    "path": "08_lab_ctf/lab.md", "source_id": "s3",
                    "source_version_id": "v1", "document_id": "d3", "title": "Lab",
                    "locator": "lab.md#1", "source_type": "lab", "content_class": "lab_reasoning",
                    "environment_scope": "lab_only", "is_approved": True, "is_unsafe": False,
                    "trust_level": 2, "assessment_phase": "authorization", "content_hash": "c" * 64,
                },
            ]],
            "distances": [[0.1, 0.2, 0.05]],
        }


class Client:
    def get_collection(self, name):
        return Collection()


def test_assessment_retrieval_filters_lab_and_returns_phase_metadata(tmp_path):
    result = search_assessment_kb(
        "authorized object level authorization assessment",
        client=Client(), embedder=Embedder(), receipt_directory=tmp_path,
    )
    assert result["query_classification"]["primary"] in {"authorization_scope", "authorization_testing"}
    assert len(result["citations"]) == 2
    assert all(item["assessment_phase"] for item in result["citations"])
    assert result["filtered_count"] == 1
    assert (tmp_path / f"{result['query_id']}.json").exists()
