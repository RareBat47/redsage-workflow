import os
import threading
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/redsage.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_db_ready = False
_db_lock = threading.Lock()


def ensure_db_ready():
    """Run schema create/ALTER at most once per process.

    Test clients and non-lifespan callers may open a request without FastAPI
    startup hooks, so the first ``get_db()`` still bootstraps the schema.
    Subsequent requests skip inspect/DDL entirely.
    """
    global _db_ready
    if _db_ready:
        return
    with _db_lock:
        if _db_ready:
            return
        init_db()
        _db_ready = True


def get_db():
    ensure_db_ready()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.models import schema  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        columns = {column["name"] for column in inspect(engine).get_columns("workflow_proposals")}
        if "created_task_id" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE workflow_proposals ADD COLUMN created_task_id VARCHAR"))
        asset_columns = {column["name"] for column in inspect(engine).get_columns("assets")}
        if "source_task_id" not in asset_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE assets ADD COLUMN source_task_id VARCHAR"))
        project_columns = {column["name"] for column in inspect(engine).get_columns("projects")}
        if "brief" not in project_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE projects ADD COLUMN brief TEXT"))
        evidence_columns = {column["name"] for column in inspect(engine).get_columns("evidence")}
        if "step_id" not in evidence_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE evidence ADD COLUMN step_id VARCHAR"))
        phase_columns = {column["name"] for column in inspect(engine).get_columns("phases")}
        for column_name, column_type in (("is_archived", "BOOLEAN"), ("archived_at", "DATETIME"), ("archived_by", "VARCHAR")):
            if column_name not in phase_columns:
                with engine.begin() as connection:
                    default = " DEFAULT 0" if column_name == "is_archived" else ""
                    connection.execute(text(f"ALTER TABLE phases ADD COLUMN {column_name} {column_type}{default}"))
            elif column_name == "is_archived":
                with engine.begin() as connection:
                    connection.execute(text("UPDATE phases SET is_archived = 0 WHERE is_archived IS NULL"))
        task_columns = {column["name"] for column in inspect(engine).get_columns("tasks")}
        for column_name, column_type in (("is_archived", "BOOLEAN"), ("archived_at", "DATETIME"), ("archived_by", "VARCHAR")):
            if column_name not in task_columns:
                with engine.begin() as connection:
                    default = " DEFAULT 0" if column_name == "is_archived" else ""
                    connection.execute(text(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}{default}"))
            elif column_name == "is_archived":
                with engine.begin() as connection:
                    connection.execute(text("UPDATE tasks SET is_archived = 0 WHERE is_archived IS NULL"))
        step_columns = {column["name"] for column in inspect(engine).get_columns("task_steps")}
        for column_name, column_type in (("archived_at", "DATETIME"), ("archived_by", "VARCHAR")):
            if column_name not in step_columns:
                with engine.begin() as connection:
                    connection.execute(text(f"ALTER TABLE task_steps ADD COLUMN {column_name} {column_type}"))
