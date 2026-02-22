# RUSS Development Guidelines

Auto-generated from feature plans. Last updated: 2026-02-22

## Active Technologies

- **Language**: Python 3.11+
- **LLM Inference**: Ollama (local HTTP at localhost:11434)
- **Models**: llama3.2 (generation), nomic-embed-text (embeddings), llama-guard3:1b (safety)
- **Vector Store**: ChromaDB (PersistentClient, per-PDF collections)
- **Keyword Search**: rank_bm25 (BM25Okapi)
- **Re-ranker**: bge-reranker-base via sentence-transformers
- **Orchestration**: LangChain (EnsembleRetriever, ChatOllama, OllamaEmbeddings)
- **PDF Parsing**: Marker (primary), PyMuPDF/pymupdf4llm (fallback)
- **UI**: Streamlit (chat + file upload)
- **Schemas**: Pydantic v2
- **Testing**: pytest (mock Ollama, no network)

## Project Structure

```text
src/
├── config/          # Settings (BaseSettings + .env), prompts
├── models/          # Pydantic schemas (Document, Chunk, Citation, ChatMessage)
├── ingestion/       # PDF parsing, chunking, embeddings
├── retrieval/       # ChromaDB, BM25, hybrid retriever, reranker
├── generation/      # LLM client, RAG chain, grounding/citations
├── safety/          # llama-guard3 input filtering
└── utils/           # Shared helpers

app.py               # Streamlit entry point
tests/               # unit/, integration/, contract/
data/chromadb/       # Persisted vector store
data/uploads/        # Uploaded PDFs
```

## Commands

```bash
# Run application
streamlit run app.py

# Run tests
pytest tests/ -v

# Pull required models
ollama pull llama3.2 && ollama pull nomic-embed-text && ollama pull llama-guard3:1b
```

## Code Style

- Pydantic models for all inter-module data transfer
- Type hints on all public functions
- Configuration via `src/config/settings.py` (no hardcoded values in pipeline modules)
- All HTTP calls to localhost only (air-gapped)

## Recent Changes

- **001-rag-tutor-system**: Initial RAG tutoring system — PDF ingestion, hybrid retrieval, cited generation, safety filtering, Streamlit chat UI

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
