"""Migrate legacy SQLite evidence rows to filesystem-backed artifacts."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database import DATABASE_URL
from backend.services.artifact_manager import save_artifact
from backend.services.cohere_service import redact_sensitive_data


def database_path() -> Path:
    prefix = "sqlite:///"
    if not DATABASE_URL.startswith(prefix):
        raise RuntimeError("Day-2 migration requires a SQLite DATABASE_URL")
    return Path(DATABASE_URL[len(prefix):]).resolve()


def migrate() -> tuple[int, int]:
    path = database_path()
    if not path.exists():
        print("No existing database to migrate. migrated_count=0 skipped_count=0")
        return 0, 0
    connection = sqlite3.connect(path)
    migrated = skipped = 0
    try:
        table_info = connection.execute("PRAGMA table_info(evidence)").fetchall()
        columns = {row[1] for row in table_info}
        additions = {
            "evidence_type": "TEXT DEFAULT 'TERMINAL_LOG'",
            "file_path": "TEXT",
            "file_size_bytes": "INTEGER DEFAULT 0",
            "redacted_excerpt": "TEXT DEFAULT ''",
        }
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(f"ALTER TABLE evidence ADD COLUMN {name} {definition}")
        # Day-1 created raw_content as NOT NULL. Rebuild only that legacy table
        # shape so artifact-only inserts can omit the compatibility column.
        raw_content_not_null = any(row[1] == "raw_content" and row[3] for row in table_info)
        if raw_content_not_null:
            connection.execute("PRAGMA foreign_keys=OFF")
            connection.execute("ALTER TABLE evidence RENAME TO evidence_day1_backup")
            connection.execute("""
                CREATE TABLE evidence (
                    id VARCHAR PRIMARY KEY,
                    project_id VARCHAR NOT NULL REFERENCES projects(id),
                    task_id VARCHAR NOT NULL REFERENCES tasks(id),
                    raw_content TEXT,
                    evidence_type VARCHAR NOT NULL DEFAULT 'TERMINAL_LOG',
                    file_path VARCHAR,
                    file_size_bytes INTEGER NOT NULL DEFAULT 0,
                    sha256_hash VARCHAR(64) NOT NULL DEFAULT '',
                    redacted_excerpt TEXT NOT NULL DEFAULT '',
                    created_at DATETIME
                )
            """)
            connection.execute("""
                INSERT INTO evidence
                (id, project_id, task_id, raw_content, sha256_hash, created_at,
                 evidence_type, file_path, file_size_bytes, redacted_excerpt)
                SELECT id, project_id, task_id, raw_content, sha256_hash, created_at,
                       evidence_type, file_path, file_size_bytes, redacted_excerpt
                FROM evidence_day1_backup
            """)
            connection.execute("DROP TABLE evidence_day1_backup")
            connection.execute("PRAGMA foreign_keys=ON")
        rows = connection.execute("SELECT id, project_id, raw_content, file_path FROM evidence").fetchall()
        for evidence_id, project_id, raw_content, file_path in rows:
            if file_path:
                if raw_content is not None:
                    connection.execute("UPDATE evidence SET raw_content = NULL WHERE id = ?", (evidence_id,))
                skipped += 1
                continue
            if raw_content is None:
                skipped += 1
                continue
            relative_path, size, digest, filename = save_artifact(project_id, evidence_id, raw_content)
            excerpt = redact_sensitive_data(raw_content[:800])
            connection.execute(
                "UPDATE evidence SET evidence_type = ?, file_path = ?, file_size_bytes = ?, sha256_hash = ?, redacted_excerpt = ?, raw_content = NULL WHERE id = ?",
                ("TERMINAL_LOG", relative_path, size, digest, excerpt, evidence_id),
            )
            migrated += 1
        connection.commit()
    finally:
        connection.close()
    print(f"Migration complete: migrated_count={migrated} skipped_count={skipped}")
    return migrated, skipped


if __name__ == "__main__":
    migrate()
