"""Test isolation for the public release.

A fresh checkout has no `data/redsage.db`, so the suite must not depend on a
pre-existing database. This fixture:

  1. Points DATABASE_URL at a fresh temporary SQLite file before any backend
     module is imported, and
  2. Creates the schema on that engine.

It also clears Cohere keys so tests never make outbound calls.
"""

import os
import tempfile
from pathlib import Path

_TMP_DB = Path(tempfile.mkdtemp(prefix="redsage_test_")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["CO_API_KEY"] = ""
os.environ["COHERE_API_KEY"] = ""

from backend.database import engine  # noqa: E402
from backend.models import schema  # noqa: E402,F401  (registers tables)

schema.Base.metadata.create_all(bind=engine)  # noqa: E402
