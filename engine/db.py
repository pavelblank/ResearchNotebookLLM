"""
ChromaDB vector store manager.
Stores all notebooks as named collections.
"""

import chromadb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "chroma"

_client = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(DB_PATH))
    return _client


def get_or_create_notebook(name: str):
    """Returns a ChromaDB collection (notebook)."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    return get_client().get_or_create_collection(
        name=safe,
        metadata={"hnsw:space": "cosine", "display_name": name}
    )


def list_notebooks():
    cols = get_client().list_collections()
    return [
        {
            "id": c.name,
            "name": c.metadata.get("display_name", c.name),
            "count": c.count()
        }
        for c in cols
    ]


def delete_notebook(name: str):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    get_client().delete_collection(safe)


def add_chunks(notebook_name: str, chunks: list[dict]):
    """
    chunks = [{"id": str, "text": str, "metadata": dict}]
    """
    col = get_or_create_notebook(notebook_name)
    col.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c.get("metadata", {}) for c in chunks]
    )


def query_chunks(notebook_name: str, query: str, n: int = 8,
                 source_id: str = None, source_ids: list = None):
    """Returns top-n relevant chunks, optionally filtered to one or more sources."""
    col = get_or_create_notebook(notebook_name)
    if col.count() == 0:
        return []
    kwargs = {"query_texts": [query], "n_results": min(n, col.count())}
    # Build where clause: multi-source uses $in operator
    if source_ids and len(source_ids) == 1:
        kwargs["where"] = {"source_id": source_ids[0]}
    elif source_ids and len(source_ids) > 1:
        kwargs["where"] = {"source_id": {"$in": list(source_ids)}}
    elif source_id:
        kwargs["where"] = {"source_id": source_id}
    results = col.query(**kwargs)
    docs  = results["documents"][0]
    metas = results["metadatas"][0]
    return [{"text": d, "meta": m} for d, m in zip(docs, metas)]


def delete_source(notebook_name: str, source_id: str) -> int:
    """Delete all chunks for a source_id. Returns number of chunks deleted."""
    col = get_or_create_notebook(notebook_name)
    # Get IDs first so we can return a count
    results = col.get(where={"source_id": source_id})
    ids = results.get("ids") or []
    if ids:
        col.delete(ids=ids)
    return len(ids)


def get_source_title(notebook_name: str, source_id: str) -> str:
    """Return the title stored for a source_id, or empty string."""
    col = get_or_create_notebook(notebook_name)
    # Note: ChromaDB get() has no limit parameter — fetch all and take first
    results = col.get(where={"source_id": source_id}, include=["metadatas"])
    metas = results.get("metadatas") or []
    if metas:
        return metas[0].get("title", "")
    return ""


def list_sources(notebook_name: str):
    """List unique sources in a notebook."""
    col = get_or_create_notebook(notebook_name)
    if col.count() == 0:
        return []
    all_data = col.get(include=["metadatas"])
    seen = set()
    sources = []
    for m in all_data["metadatas"]:
        key = m.get("source_id", "unknown")
        if key not in seen:
            seen.add(key)
            sources.append({
                "source_id": key,
                "title": m.get("title", key),
                "type": m.get("type", "unknown")
            })
    return sources
