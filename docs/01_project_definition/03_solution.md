## Solution Overview

Build a small, local RAG system with these components:
- PDF ingestion: extract text and tables from uploaded PDFs (Marker or PyMuPDF).
- Chunking: paragraph-aware text chunking with overlap to preserve context.
- Embeddings: sentence-transformer model to embed chunks locally.
- Vector store: ChromaDB persisted under `data/chromadb`.
- Hybrid retrieval: combine BM25 (keyword) and semantic similarity for robust
	retrieval.
- Local LLM: invoke Ollama via HTTP to generate answers from retrieved
	context and a compact system prompt.
- Grounding: extract and format citations (source file + chunk ID + text
	snippets) and append a citation footer to every answer.

User flow: upload PDFs → index them → ask questions → receive answers with
inline citations and a footer listing sources used.
