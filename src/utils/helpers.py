from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional


def slugify(text: str) -> str:
	text = text.lower()
	text = re.sub(r"[^a-z0-9]+", "-", text)
	return text.strip("-")


def sha256_short(path: Path, length: int = 8) -> str:
	h = hashlib.sha256()
	with path.open("rb") as fh:
		while True:
			chunk = fh.read(8192)
			if not chunk:
				break
			h.update(chunk)
	return h.hexdigest()[:length]


def collection_name_for_file(path: Path) -> str:
	"""Deterministic collection name: {slug}-{sha256[:8]}

	Uses filename (not full path) for slug, short sha256 of file bytes for uniqueness.
	"""
	slug = slugify(path.stem)
	short = sha256_short(path)
	return f"{slug}-{short}"


def is_pdf(path: Path) -> bool:
	return path.suffix.lower() == ".pdf"


def validate_file_size(path: Path, max_mb: int) -> Optional[str]:
	"""Return error message string if file too large, else None."""
	size_mb = path.stat().st_size / (1024 * 1024)
	if size_mb > max_mb:
		return f"File size {size_mb:.1f} MB exceeds maximum of {max_mb} MB"
	return None

