## Problem

Cadets and instructors need an offline, secure tutoring assistant that can
ingest course materials (PDF textbooks and curriculum) and answer questions
accurately with source-backed citations. Cloud LLMs and external services are
not permitted; the solution must run locally (air-gapped) using a locally
hosted model (via Ollama). PDFs contain text and tables only — no OCR for
images is required.

Key pain points:
- Long manuals/textbooks are hard to search manually.
- Students need concise, citation-backed answers to support learning and
	assessments.
- Organizational policy requires on-premises-only operation.

This project builds a small RAG-based tutor focused on these constraints.
