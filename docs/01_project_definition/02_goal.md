## Goals

Primary goals:
- Provide an offline RAG tutor that accepts PDF curriculum and returns
	concise, citation-backed answers.
- Support only text and tables from PDFs (no image OCR).
- Run locally using Ollama-hosted models; keep all data and models on-premises.

Non-goals / constraints:
- No integration with cloud LLM APIs.
- No image/diagram analysis (text only)
- No model fine-tuning
- No persistent chat history
- No user authentication
- Single-machine deployment (no distributed setup)