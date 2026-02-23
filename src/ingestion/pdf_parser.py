"""PDF parsing module supporting Marker (primary) and PyMuPDF (fallback)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

# Large PDF threshold for warnings
LARGE_PDF_THRESHOLD = 200


def parse_pdf(file_path: Path, parser: str = "marker") -> Tuple[str, int]:
    """Parse a PDF and return (markdown_text, page_count).

    Attempts Marker parser first (if requested), then falls back to pymupdf4llm, then to PyMuPDF basic extraction.
    Raises ValueError on non-PDF or irrecoverable parse errors.
    """
    if not file_path.exists():
        raise ValueError("file not found")
    if file_path.suffix.lower() != ".pdf":
        raise ValueError("not a PDF file")

    # Warn for large PDFs
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 50:
        logger.warning(f"Large PDF ({file_size_mb:.1f}MB) may take longer to process")

    # Try marker-pdf (optional dependency)
    if parser == "marker":
        try:
            from marker_pdf import PdfConverter

            conv = PdfConverter()
            model_dict = conv.create_model_dict(str(file_path))
            # model_dict expected to contain 'markdown' and 'page_count' per spec
            md = model_dict.get("markdown") or model_dict.get("text") or ""
            page_count = int(model_dict.get("page_count", 0) or 0)
            return md, page_count
        except Exception:
            # fall through to other parsers
            pass

    # Try pymupdf4llm
    try:
        import pymupdf4llm

        md_pages = pymupdf4llm.to_markdown(str(file_path), page_chunks=True)
        # md_pages may be list of pages; join with page separators
        if isinstance(md_pages, (list, tuple)):
            md = "\n\n".join(md_pages)
            page_count = len(md_pages)
        else:
            md = md_pages
            page_count = md.count('\f') + 1
        return md, page_count
    except Exception:
        pass

    # Fallback: PyMuPDF (fitz) basic text extraction
    try:
        import fitz

        doc = fitz.open(str(file_path))
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        md = "\n\n".join(pages)
        return md, len(pages)
    except Exception as exc:
        raise ValueError(f"unable to parse PDF: {exc}")
