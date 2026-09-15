import pytest

from KB.index_compatibility import reconcile_collection_ids, validate_collection_metadata


class Collection:
    def __init__(self, ids):
        self.ids = ids
        self.deleted = []

    def count(self):
        return len(self.ids)

    def get(self, **kwargs):
        return {"ids": self.ids[kwargs["offset"]:kwargs["offset"] + kwargs["limit"]]}

    def delete(self, ids):
        self.deleted.extend(ids)


def test_reconcile_reports_stale_and_missing_ids_without_mutation():
    result = reconcile_collection_ids({"a", "b"}, Collection(["a", "stale"]))
    assert result == {"stale_ids": ["stale"], "missing_ids": ["b"], "deleted_ids": []}


def test_reconcile_can_delete_only_explicit_stale_ids():
    collection = Collection(["a", "stale"])
    result = reconcile_collection_ids({"a"}, collection, delete_stale=True)
    assert result["deleted_ids"] == ["stale"]
    assert collection.deleted == ["stale"]


def test_collection_metadata_requires_matching_fields():
    with pytest.raises(ValueError, match="policy_version"):
        validate_collection_metadata(
            {"model": "m", "metadata_schema_version": "s", "source_manifest": "p"},
            model="m", schema_version="s", policy_version="p", manifest_path="p",
        )
