"""Document ingestion pipeline orchestrator."""

from __future__ import annotations

import logging
from pathlib import Path

from src.config.settings import settings
from src.ingestion.chunking import chunk_document
from src.ingestion.embeddings import embed_and_store
from src.ingestion.pdf_parser import parse_pdf
from src.models.schemas import Document, DocumentStatus
from src.retrieval.bm25_index import BM25Index
from src.retrieval.hybrid_retriever import get_bm25_index
from src.utils.helpers import collection_name_for_file
from src.retrieval.vector_store import get_or_create_collection

logger = logging.getLogger(__name__)


def ingest_document(file_path: Path, file_name: str) -> Document:
    """Orchestrate full document ingestion pipeline.

    Coordinates: parse → chunk → embed → store

    Args:
        file_path: Path to uploaded PDF file
        file_name: Original filename for metadata

    Returns:
        Document object with final status and metadata

    Raises:
        Exception is caught and stored in Document.error_message
    """
    document = Document(
        file_name=file_name,
        status=DocumentStatus.PENDING,
    )

    try:
        # Generate deterministic collection name
        collection_name = collection_name_for_file(file_path)
        document.collection_name = collection_name

        # Update status to PROCESSING
        document.status = DocumentStatus.PROCESSING

        # Parse PDF
        logger.info(f"Parsing PDF: {file_name}")
        markdown_text, page_count = parse_pdf(file_path, parser=settings.pdf_parser)
        document.total_pages = page_count

        # Warn for large PDFs
        if page_count > 200:
            logger.warning(f"Document has {page_count} pages (guideline: <200). Processing may be slow.")

        # Chunk document
        logger.info(f"Chunking document: {file_name}")
        chunks = chunk_document(
            text=markdown_text,
            file_name=file_name,
            collection_name=collection_name,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        if not chunks:
            raise ValueError("Document produced no chunks after parsing")

        # Build BM25 index for this collection
        logger.info(f"Building BM25 index for {len(chunks)} chunks")
        bm25_index = get_bm25_index(collection_name)
        bm25_index.build_index(chunks)

        # Embed and store
        logger.info(f"Embedding and storing {len(chunks)} chunks")
        embed_and_store(chunks, collection_name)

        # Mark as ready
        document.status = DocumentStatus.READY
        logger.info(f"Successfully ingested: {file_name} ({page_count} pages, {len(chunks)} chunks)")

    except Exception as e:
        logger.error(f"Ingestion failed for {file_name}: {e}")
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)

    return document

    return document
