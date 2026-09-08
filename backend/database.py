import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/redsage.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
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
