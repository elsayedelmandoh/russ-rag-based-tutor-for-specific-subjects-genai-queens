"""Document chunking with metadata injection."""

from __future__ import annotations

from typing import List
from pathlib import Path

from src.models.schemas import Chunk


def chunk_document(text: str, file_name: str, collection_name: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Chunk]:
    """Chunk text into `Chunk` objects using simple character-based splitter.

    This avoids a hard dependency on LangChain while producing predictable chunks.
    """
    if not text:
        return []

    chunks: List[Chunk] = []
    start = 0
    chunk_index = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        piece = text[start:end]
        # Attempt to assign a page number if a page break exists
        page_number = None
        if "\f" in piece:
            # crude heuristic: count page breaks before start
            page_number = text[:start].count("\f") + 1

        chunks.append(
            Chunk(
                text=piece,
                source_document=file_name,
                page_number=page_number,
                section_heading=None,
                chunk_index=chunk_index,
                collection_name=collection_name,
            )
        )
        chunk_index += 1
        start = end - chunk_overlap if end < text_len else end

    return chunks
