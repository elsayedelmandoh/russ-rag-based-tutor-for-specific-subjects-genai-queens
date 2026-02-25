"""Citation extraction and source grounding."""

from __future__ import annotations

import logging
from typing import List

from src.config.prompts import CITATION_TEMPLATE
from src.models.schemas import Citation, RetrievalResult

logger = logging.getLogger(__name__)


def extract_citations(retrieval_results: List[RetrievalResult]) -> List[Citation]:
    """Extract citations from retrieval results.

    Args:
        retrieval_results: List of RetrievalResult objects from retrieval

    Returns:
        List of Citation objects with source metadata
    """
    citations = []
    for result in retrieval_results:
        chunk = result.chunk
        citation = Citation(
            source_document=chunk.source_document,
            page_number=chunk.page_number,
            text_snippet=chunk.text[:200] if chunk.text else "",  # First 200 chars
            relevance_score=result.score,
        )
        citations.append(citation)

    return citations


def format_citations(citations: List[Citation]) -> str:
    """Format citations for display in response footer.

    Args:
        citations: List of Citation objects

    Returns:
        Markdown-formatted citation footer
    """
    if not citations:
        return ""

    # Deduplicate by source_document to avoid redundant citations
    seen = set()
    unique_citations = []
    for cite in citations:
        key = (cite.source_document, cite.page_number)
        if key not in seen:
            seen.add(key)
            unique_citations.append(cite)

    # Format citations
    formatted = [
        CITATION_TEMPLATE.format(
            source=cite.source_document,
            page=cite.page_number or "?"
        )
        for cite in unique_citations
    ]

    return "\n\n**Sources:** " + " ".join(formatted)


def build_context(retrieval_results: List[RetrievalResult]) -> str:
    """Build context string from retrieved chunks for LLM prompt.

    Args:
        retrieval_results: List of RetrievalResult objects

    Returns:
        Formatted context string for inclusion in LLM prompt
    """
    if not retrieval_results:
        return ""

    context_parts = []
    for i, result in enumerate(retrieval_results, 1):
        chunk = result.chunk
        source = chunk.source_document
        page = chunk.page_number or "?"
        header = f"[Source: {source} (p.{page})]"
        context_parts.append(f"{header}\n{chunk.text}")

    return "\n\n".join(context_parts)
