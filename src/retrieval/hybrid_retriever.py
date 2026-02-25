"""Hybrid BM25 + semantic search with reranking."""

from __future__ import annotations

import logging
from typing import List

from src.config.settings import settings
from src.ingestion.embeddings import generate_embeddings
from src.models.schemas import Chunk, RetrievalResult
from src.retrieval.bm25_index import BM25Index
from src.retrieval.reranker import rerank
from src.retrieval.vector_store import query_collection

logger = logging.getLogger(__name__)

# Global BM25 index cache
_bm25_indices = {}


def get_bm25_index(collection_name: str) -> BM25Index:
    """Get or create BM25 index for a collection."""
    if collection_name not in _bm25_indices:
        index = BM25Index()
        _bm25_indices[collection_name] = index
    return _bm25_indices[collection_name]


class HybridRetriever:
    """Hybrid retriever combining BM25 + semantic search with reranking."""

    def __init__(self):
        pass

    def retrieve(self, query: str, collection_names: List[str], k: int = None) -> List[RetrievalResult]:
        """Retrieve top-k results using hybrid search.

        Combines BM25 (keyword) and semantic (vector) retrieval, optionally reranks with cross-encoder.

        Args:
            query: User query string
            collection_names: List of ChromaDB collection names to search
            k: Number of results (default from settings.retrieval_k)

        Returns:
            List of RetrievalResult objects ranked by score
        """
        k = k or settings.retrieval_k

        if not collection_names:
            logger.warning("No collections to retrieve from")
            return []

        all_results = []

        for collection_name in collection_names:
            # BM25 search
            bm25_index = get_bm25_index(collection_name)
            bm25_results = bm25_index.search(query, k=k)
            logger.debug(f"BM25 search for '{collection_name}': {len(bm25_results)} results")

            # Semantic search (vector similarity via ChromaDB)
            semantic_results = self._semantic_search(query, collection_name, k=k)
            logger.debug(f"Semantic search for '{collection_name}': {len(semantic_results)} results")

            # Merge and deduplicate by chunk_id
            merged = self._merge_results(bm25_results, semantic_results, k=k)
            all_results.extend(merged)

        # Deduplicate across collections
        dedup_map = {}
        for result in all_results:
            key = result.chunk.chunk_id
            if key not in dedup_map or result.score > dedup_map[key].score:
                dedup_map[key] = result

        unique_results = list(dedup_map.values())

        # Rerank with cross-encoder
        top_n = settings.rerank_top_n
        reranked = rerank(query, [r.chunk for r in unique_results], top_n=top_n)

        logger.debug(f"Hybrid retrieval: {len(all_results)} total → {len(unique_results)} unique → {len(reranked)} reranked")
        return reranked

    def _semantic_search(self, query: str, collection_name: str, k: int = 10) -> List[RetrievalResult]:
        """Search using vector similarity via ChromaDB.
        
        Args:
            query: Search query
            collection_name: Collection to query
            k: Number of results
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            logger.debug(f"Starting semantic search for query: {query[:50]}...")
            
            # Generate embedding for query
            embeddings = generate_embeddings([query])
            if not embeddings or not embeddings[0]:
                logger.warning("Failed to generate query embedding")
                return []
            
            query_embedding = embeddings[0]
            
            # Query ChromaDB with embedding
            results = query_collection(collection_name, query_embedding, k=k)
            logger.debug(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def _merge_results(self, bm25_results: List[Chunk], semantic_results: List[RetrievalResult], k: int) -> List[RetrievalResult]:
        """Merge BM25 and semantic results using ensemble weights."""
        # Create result map
        result_map = {}

        # Add BM25 results with weight
        for i, chunk in enumerate(bm25_results):
            score = (k - i) / k * settings.bm25_weight  # Rank-based scoring
            result_map[chunk.chunk_id] = RetrievalResult(chunk=chunk, score=score)

        # Add/update with semantic results with weight
        for result in semantic_results:
            key = result.chunk.chunk_id
            semantic_score = result.score * settings.semantic_weight
            if key in result_map:
                # Combine scores
                result_map[key].score += semantic_score
            else:
                result_map[key] = RetrievalResult(chunk=result.chunk, score=semantic_score)

        # Sort by combined score
        merged = sorted(result_map.values(), key=lambda r: r.score, reverse=True)
        return merged[:k]
