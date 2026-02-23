"""Embedding generation and storage pipeline."""

from __future__ import annotations

import logging
from typing import List

import httpx

from src.config.settings import settings
from src.models.schemas import Chunk
from src.retrieval.vector_store import add_chunks, get_or_create_collection

logger = logging.getLogger(__name__)


def embed_and_store(chunks: List[Chunk], collection_name: str) -> None:
    """Generate embeddings for chunks and store in ChromaDB.

    Args:
        chunks: List of Chunk objects to embed
        collection_name: Target ChromaDB collection
    """
    if not chunks:
        logger.warning("No chunks to embed")
        return

    # Generate embeddings via Ollama
    embeddings = generate_embeddings([chunk.text for chunk in chunks])

    if not embeddings or len(embeddings) != len(chunks):
        raise ValueError(f"Embedding generation failed: got {len(embeddings)} embeddings for {len(chunks)} chunks")

    # Store in ChromaDB
    add_chunks_with_embeddings(collection_name, chunks, embeddings)

    logger.info(f"Embedded and stored {len(chunks)} chunks in '{collection_name}'")


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using Ollama.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    embeddings = []
    for text in texts:
        try:
            # Call Ollama /api/embed endpoint
            url = f"{settings.ollama_base_url.rstrip('/')}/api/embed"
            payload = {
                "model": settings.embedding_model,
                "input": text,
            }
            resp = httpx.post(url, json=payload, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

            # Extract embedding vector
            if "embeddings" in data and data["embeddings"]:
                embeddings.append(data["embeddings"][0])
            else:
                logger.warning(f"No embedding in response for text: {text[:50]}...")
                embeddings.append([0.0] * 768)  # Fallback zero vector

        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            embeddings.append([0.0] * 768)  # Fallback zero vector

    return embeddings


def add_chunks_with_embeddings(collection_name: str, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
    """Add chunks with embeddings to ChromaDB collection.

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
