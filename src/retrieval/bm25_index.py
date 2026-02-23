"""BM25 keyword search index for hybrid retrieval."""

from __future__ import annotations

import logging
from typing import List

from rank_bm25 import BM25Okapi

from src.models.schemas import Chunk

logger = logging.getLogger(__name__)


class BM25Index:
    """BM25 index for keyword-based retrieval."""

    def __init__(self):
        self.bm25 = None
        self.chunks = []
        self.tokenized_corpus = []

    def build_index(self, chunks: List[Chunk]) -> None:
        """Build BM25 index from chunks.

        Args:
            chunks: List of Chunk objects to index
        """
        if not chunks:
            logger.warning("No chunks to index")
            return

        self.chunks = chunks

        # Tokenize documents (simple whitespace split)
        self.tokenized_corpus = [chunk.text.lower().split() for chunk in chunks]

        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info(f"Built BM25 index with {len(chunks)} documents")

    def search(self, query: str, k: int = 10) -> List[Chunk]:
        """Search for top-k chunks matching query.

        Args:
            query: Search query string
            k: Number of top results to return

        Returns:
            List of Chunk objects ranked by BM25 score
        """
        if not self.bm25 or not self.chunks:
            logger.warning("BM25 index not built")
            return []

        # Tokenize query
        query_tokens = query.lower().split()

        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Rank chunks by score
        ranked = sorted(
            enumerate(self.chunks),
            key=lambda x: scores[x[0]],
            reverse=True
        )

        # Return top-k chunks
        return [chunk for _, chunk in ranked[:k]]
