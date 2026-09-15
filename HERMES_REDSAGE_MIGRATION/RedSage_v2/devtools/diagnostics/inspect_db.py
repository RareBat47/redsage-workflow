"""Read-only DB inspection script - safe to run, makes no modifications."""
import chromadb
import sqlite3
from pathlib import Path

chroma_path = r"D:\HIGH LEVELS OF WORKS\RedSage_v2\data\chroma"
db_path = r"D:\HIGH LEVELS OF WORKS\RedSage_v2\data\redsage.db"

# ChromaDB
print("=== ChromaDB Collections ===")
client = chromadb.PersistentClient(path=chroma_path)
collections = client.list_collections()
for col in collections:
    print(f"  {col.name}: {col.count()} chunks")

# Quick sample query on first collection
if collections:
    active = collections[0]
    print(f"\n  [Sample] Querying '{active.name}' with dummy vector...")
    dim = 8  # deterministic embedder uses 8-dim vectors
    result = active.query(query_embeddings=[[0.5]*dim], n_results=2)
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        print(f"    chunk {i}: title={meta.get('title','?')}, source={meta.get('source','?')}")
        print(f"      snippet: {doc[:120].strip()}...")

# SQLite
print("\n=== SQLite Tables ===")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()
for (t,) in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {count} rows")

print("\n=== SQLite Schema (first 3 tables) ===")
for (t,) in tables[:3]:
    schema = conn.execute(
        f"SELECT sql FROM sqlite_master WHERE name=?", (t,)
    ).fetchone()
    print(f"\n-- {t} --")
    print(schema[0] if schema else "  (no schema)")

conn.close()
print("\nDatabases verified OK.")
