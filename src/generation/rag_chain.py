"""RAG chain orchestration: retrieve → rerank → generate."""

from __future__ import annotations

import logging
from typing import List

from src.config.prompts import NO_DOCUMENTS_PROMPT, RAG_SYSTEM_PROMPT, SAFETY_BLOCK_RESPONSE
from src.generation.grounding import build_context, extract_citations, format_citations
from src.generation.llm_client import get_llm
from src.models.schemas import ChatMessage, MessageRole
from src.retrieval.hybrid_retriever import HybridRetriever
from src.safety.guardrail import check_safety, HARD_BLOCK_CATEGORIES

logger = logging.getLogger(__name__)


def ask_question(
    query: str,
    collection_names: List[str],
    history: List[ChatMessage] = None,
) -> ChatMessage:
    """Ask a question and get a cited answer.

    Orchestrates: retrieve → rerank → build context → generate → extract citations

    Args:
        query: User's question
        collection_names: List of ChromaDB collections to search (by subject)
        history: Optional conversation history for context

    Returns:
        ChatMessage with role=ASSISTANT, content (answer), and citations
    """
    history = history or []

    # Safety check
    logger.info(f"Checking query safety...")
    safety_result = check_safety(query)

    if not safety_result.is_safe and any(cat in HARD_BLOCK_CATEGORIES for cat in safety_result.violated_categories):
        logger.warning(f"Query blocked by safety filter: {safety_result.violated_categories}")
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=SAFETY_BLOCK_RESPONSE,
            citations=[],
            safety_status="BLOCKED",
        )

    if not collection_names:
        # No documents uploaded
        logger.warning("No collections to retrieve from")
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=NO_DOCUMENTS_PROMPT,
            citations=[],
        )

    # Retrieve relevant chunks
    logger.info(f"Retrieving for query: {query[:100]}...")
    retriever = HybridRetriever()
    retrieval_results = retriever.retrieve(query, collection_names)

    if not retrieval_results:
        logger.warning("No relevant sources found")
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content="I couldn't find relevant information in the uploaded documents.",
            citations=[],
        )

    # Extract citations
    citations = extract_citations(retrieval_results)

    # Build context for LLM
    context = build_context(retrieval_results)

    # Build prompt with conversation history
    messages = []

    # Add system prompt
    messages.append({"role": "system", "content": RAG_SYSTEM_PROMPT})

    # Add conversation history
    for msg in history:
        messages.append({"role": msg.role.value, "content": msg.content})

    # Add current query with context
    prompt = f"Context from documents:\n\n{context}\n\n---\n\nQuestion: {query}"
    messages.append({"role": "user", "content": prompt})

    # Generate answer
    logger.info("Generating answer...")
    try:
        llm = get_llm()
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        answer = "Sorry, I encountered an error generating a response."

    # Format with citations
    citation_footer = format_citations(citations)
    full_answer = answer + citation_footer

    return ChatMessage(
        role=MessageRole.ASSISTANT,
        content=full_answer,
        citations=citations,
    )
