from backend.services.recovery_service import reconcile_storage_and_db


def test_recovery_removes_stale_atomic_files(tmp_path):
    artifact_dir = tmp_path / "project" / "artifacts"
    artifact_dir.mkdir(parents=True)
    stale = artifact_dir / ".EVID-1.txt.tmp"
    stale.write_text("incomplete", encoding="utf-8")

    result = reconcile_storage_and_db(None, tmp_path)

    assert result == {"cleaned_tmp_files": 1, "missing_records": 0}
    assert not stale.exists()
