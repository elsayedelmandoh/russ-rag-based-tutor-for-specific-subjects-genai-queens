"""Cross-encoder reranking for retrieval results."""

from __future__ import annotations

import logging
from typing import List

from sentence_transformers import CrossEncoder

from src.config.settings import settings
from src.models.schemas import Chunk, RetrievalResult

logger = logging.getLogger(__name__)

# Cache model in module to avoid reloading
_reranker_model = None


def get_reranker():
    """Lazy-load cross-encoder model."""
    global _reranker_model
    if _reranker_model is None:
        logger.info(f"Loading reranker model: {settings.reranker_model}")
        _reranker_model = CrossEncoder(settings.reranker_model)
    return _reranker_model


def rerank(query: str, chunks: List[Chunk], top_n: int = 5) -> List[RetrievalResult]:
    """Rerank chunks using cross-encoder and return top-n.

    Args:
        query: Search query
        chunks: List of candidate chunks
        top_n: Number of top-ranked results to return

    Returns:
        List of RetrievalResult objects ranked by cross-encoder score
    """
    if not chunks:
        logger.warning("No chunks to rerank")
        return []

    try:
        model = get_reranker()

        # Prepare (query, chunk_text) pairs for reranker
        pairs = [[query, chunk.text] for chunk in chunks]

        # Get cross-encoder scores
        scores = model.predict(pairs)

        # Rank by score
        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top-n as RetrievalResult
        results = [
            RetrievalResult(chunk=chunk, score=float(score))
            for chunk, score in ranked[:top_n]
        ]

        logger.debug(f"Reranked {len(chunks)} chunks to top {len(results)}")
        return results

    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        # Fallback: return chunks as-is without scores
        return [RetrievalResult(chunk=chunk, score=0.0) for chunk in chunks[:top_n]]
