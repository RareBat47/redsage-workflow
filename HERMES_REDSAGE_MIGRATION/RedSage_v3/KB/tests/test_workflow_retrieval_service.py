from KB.workflow_retrieval_service import search_workflow_context


class Embedder:
    def embed_query(self, query):
        return [0.1, 0.2]


class Collection:
    def query(self, **kwargs):
        return {
            "ids": [["safe", "lab"]],
            "documents": [["authorization scope evidence", "lab payload"]],
            "metadatas": [[
                {"path": "09_scope_authorization/policy.md", "source_id": "s", "ordinal": 0, "content_hash": "a"},
                {"path": "08_lab_ctf/lab.md", "source_id": "l", "ordinal": 0, "content_hash": "b"},
            ]],
            "distances": [[0.1, 0.05]],
        }


class Client:
    def get_collection(self, name):
        return Collection()


def test_service_returns_citations_and_excludes_lab_by_default(tmp_path):
    result = search_workflow_context(
        "authorization scope evidence",
        embedder=Embedder(), client=Client(), receipt_directory=tmp_path,
    )
    assert len(result["citations"]) == 1
    assert result["citations"][0]["citation_id"] == "[1]"
    assert (tmp_path / f"{result['query_id']}.json").exists()
