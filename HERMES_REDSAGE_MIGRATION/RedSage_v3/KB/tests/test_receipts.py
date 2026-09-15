import json

from KB.receipts import write_retrieval_receipt


def test_receipt_hashes_query_without_storing_raw_text(tmp_path):
    receipt = write_retrieval_receipt(
        tmp_path,
        actor_type="operator",
        index_profile="workflow-cohere-v1",
        policy_version="v1",
        selected_chunk_ids=["c1"],
        query="secret problem statement",
    )
    path = tmp_path / f"{receipt['query_id']}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["query_hash"]
    assert "secret problem statement" not in path.read_text(encoding="utf-8")
    assert data["selected_chunk_ids"] == ["c1"]
