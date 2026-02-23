"""ChromaDB vector store integration for semantic search."""

from __future__ import annotations

import logging
from typing import List

from src.config.settings import settings
from src.models.schemas import Chunk, RetrievalResult

logger = logging.getLogger(__name__)


def get_or_create_collection(collection_name: str):
    """Get or create a ChromaDB collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        ChromaDB collection object
    """
    try:
        import chromadb

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
    """Add chunks to a collection without embeddings."""
    col = get_or_create_collection(collection_name)
    # Prepare ids, metadatas, documents
    ids = [c.chunk_id for c in chunks]
    docs = [c.text for c in chunks]
    metadatas = [
        {
            "source_document": c.source_document,
            "page_number": str(c.page_number) if c.page_number else "0",
            "section_heading": c.section_heading or "",
            "chunk_index": str(c.chunk_index),
        }
        for c in chunks
    ]
    try:
        # chroma api: add(documents=..., metadatas=..., ids=..., embeddings=...)
        col.add(documents=docs, metadatas=metadatas, ids=ids)
    except Exception as e:
        logger.warning(f"Failed to add chunks: {e}")
        # Some chroma clients expect different params; try with minimal args
        try:
            col.add(documents=docs, ids=ids)
        except Exception as e2:
            logger.error(f"Failed to add chunks with fallback: {e2}")


def add_chunks_with_embeddings(collection_name: str, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
    """Add chunks with precomputed embeddings to a collection.
    
    Args:
        collection_name: Target collection
        chunks: List of Chunk objects
        embeddings: List of embedding vectors
    """
    if not chunks or not embeddings:
        logger.warning("No chunks or embeddings to add")
        return

    if len(chunks) != len(embeddings):
        raise ValueError(f"Chunk count {len(chunks)} != embedding count {len(embeddings)}")

    collection = get_or_create_collection(collection_name)

    ids = [chunk.chunk_id for chunk in chunks]
    docs = [chunk.text for chunk in chunks]
    metadatas = [
        {
            "source_document": chunk.source_document,
            "page_number": str(chunk.page_number) if chunk.page_number else "0",
            "section_heading": chunk.section_heading or "",
            "chunk_index": str(chunk.chunk_index),
        }
        for chunk in chunks
    ]

    try:
        collection.add(
            ids=ids,
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info(f"Added {len(chunks)} embedded chunks to '{collection_name}'")
    except Exception as e:
        logger.error(f"Failed to add chunks to collection: {e}")
        raise


def query_collection(collection_name: str, query_embedding: List[float], k: int = 10) -> List[RetrievalResult]:
    """Query a collection using semantic search with embeddings.
    
    Args:
        collection_name: Collection to query
        query_embedding: Query embedding vector
        k: Number of results to return
        
    Returns:
        List of RetrievalResult objects
    """
    try:
        collection = get_or_create_collection(collection_name)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
        
        if not results or not results["ids"] or not results["ids"][0]:
            logger.debug(f"No results from semantic search in '{collection_name}'")
            return []
        
        # Convert results to RetrievalResult objects
        retrieval_results = []
        ids = results["ids"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(ids)
        documents = results["documents"][0] if "documents" in results else []
        metadatas = results["metadatas"][0] if "metadatas" in results else [{}] * len(ids)
        
        for i, chunk_id in enumerate(ids):
            # Convert distance to similarity score (1 - distance for cosine)
            similarity_score = 1 - distances[i] if i < len(distances) else 0.0
            
            # Reconstruct chunk from metadata and document
            chunk = Chunk(
                chunk_id=chunk_id,
                text=documents[i] if i < len(documents) else "",
                source_document=metadatas[i].get("source_document", "") if i < len(metadatas) else "",
                page_number=int(metadatas[i].get("page_number", 0)) if i < len(metadatas) else None,
                section_heading=metadatas[i].get("section_heading") if i < len(metadatas) else None,
                chunk_index=int(metadatas[i].get("chunk_index", 0)) if i < len(metadatas) else 0,
                collection_name=collection_name,
            )
            
            retrieval_results.append(RetrievalResult(chunk=chunk, score=similarity_score))
        
        return retrieval_results
    
    except Exception as e:
        logger.error(f"Query failed for collection '{collection_name}': {e}")
        return []


def delete_collection(collection_name: str):
    """Delete a collection."""
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
    """List all available collections."""
    try:
        import chromadb

        client = chromadb.PersistentClient(path=settings.chromadb_path)
        return [c.name for c in client.list_collections()]
    except Exception:
        return []
