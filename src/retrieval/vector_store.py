from __future__ import annotations

from typing import List
from src.config.settings import settings
from src.models.schemas import Chunk


def get_or_create_collection(collection_name: str):
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        client = chromadb.PersistentClient(path=settings.chromadb_path)
        # chroma collections are created on add if missing; provide wrapper
        try:
            col = client.get_collection(name=collection_name)
        except Exception:
            col = client.create_collection(name=collection_name)
        return col
    except Exception as exc:  # pragma: no cover - external dependency
        raise RuntimeError(f"chromadb not available: {exc}")


def add_chunks(collection_name: str, chunks: List[Chunk]):
    col = get_or_create_collection(collection_name)
    # Prepare ids, metadatas, documents
    ids = [c.chunk_id for c in chunks]
    docs = [c.text for c in chunks]
    metadatas = [
        {
            "source_document": c.source_document,
            "page_number": c.page_number,
            "section_heading": c.section_heading,
            "chunk_index": c.chunk_index,
        }
        for c in chunks
    ]
    try:
        # chroma api: add(documents=..., metadatas=..., ids=..., embeddings=...)
        col.add(documents=docs, metadatas=metadatas, ids=ids)
    except Exception:
        # Some chroma clients expect different params; try with minimal args
        col.add(documents=docs, ids=ids)


def delete_collection(collection_name: str):
    try:
        import chromadb

        client = chromadb.PersistentClient(path=settings.chromadb_path)
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            # older clients may require get_collection then delete
            col = client.get_collection(name=collection_name)
            col.delete()
    except Exception as exc:
        raise RuntimeError(f"chromadb not available: {exc}")


def list_collections():
    try:
        import chromadb

        client = chromadb.PersistentClient(path=settings.chromadb_path)
        return [c.name for c in client.list_collections()]
    except Exception:
        return []
