import pytest

from KB.index_compatibility import (
    validate_collection_metadata,
    validate_manifest_identity,
)


def test_matching_collection_metadata_is_accepted():
    validate_collection_metadata(
        {
            "model": "embed-english-v3.0",
            "metadata_schema_version": "assessment-v1",
            "policy_version": "assessment-v1",
            "source_manifest": "manifest.json",
        },
        model="embed-english-v3.0",
        schema_version="assessment-v1",
        policy_version="assessment-v1",
        manifest_path="manifest.json",
    )


def test_mismatched_collection_metadata_is_rejected():
    with pytest.raises(ValueError, match="model"):
        validate_collection_metadata(
            {"model": "old"},
            model="new",
            schema_version="v1",
            policy_version="v1",
            manifest_path="m.json",
        )


def test_manifest_collection_identity_is_validated():
    validate_manifest_identity({"collection_name": "expected"}, "expected")
    with pytest.raises(ValueError, match="collection"):
        validate_manifest_identity({"collection_name": "other"}, "expected")
    with pytest.raises(ValueError, match="required"):
        validate_manifest_identity({}, "expected")
