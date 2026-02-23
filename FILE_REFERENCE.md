# RUSS Project File Reference Guide

## Quick Navigation

### 🚀 Getting Started
- **[README.md](README.md)** - Main project documentation with quick start guide
- **[COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)** - What was completed and how to run
- **[setup.bat](setup.bat)** - Windows setup script (double-click to run)
- **[setup.sh](setup.sh)** - Linux/Mac setup script
- **[validate.py](validate.py)** - Validation script to check all imports work
- **[.env](.env)** - Configuration file (environment variables)

### 📚 Documentation
- **[docs/01_project_definition/00_quickstart.md](docs/01_project_definition/00_quickstart.md)** - Project overview
- **[docs/01_project_definition/01_problem.md](docs/01_project_definition/01_problem.md)** - Problem statement
- **[docs/01_project_definition/02_goal.md](docs/01_project_definition/02_goal.md)** - Project goals
- **[docs/01_project_definition/03_solution.md](docs/01_project_definition/03_solution.md)** - Solution architecture
- **[docs/01_project_definition/04_stack.md](docs/01_project_definition/04_stack.md)** - Technology stack
- **[docs/01_project_definition/05_architecture.md](docs/01_project_definition/05_architecture.md)** - Detailed architecture
- **[docs/01_project_definition/06_workflow.md](docs/01_project_definition/06_workflow.md)** - User workflows
- **[docs/01_project_definition/07_structure.md](docs/01_project_definition/07_structure.md)** - Project structure

### 💻 Application Entry Point
- **[app.py](app.py)** - Main Streamlit web application
  - Streamlit UI for PDF upload and chat
  - Subject management
  - Document status tracking
  - Conversation interface

### ⚙️ Configuration & Models

#### Configuration (`src/config/`)
- **[src/config/settings.py](src/config/settings.py)** - Environment settings using Pydantic
  - Ollama endpoints
  - Model names
  - Chunking parameters
  - Retrieval weights
  - File paths

- **[src/config/prompts.py](src/config/prompts.py)** - LLM system prompts
  - RAG system prompt
  - Citation template
  - Safety block responses
  - Default messages

#### Data Models (`src/models/`)
- **[src/models/schemas.py](src/models/schemas.py)** - Pydantic data models
  - `DocumentStatus` enum
  - `MessageRole` enum
  - `Document` - Document metadata
  - `Chunk` - Text chunks with metadata
  - `ChatMessage` - Conversation messages
  - `Citation` - Source citations
  - `RetrievalResult` - Search results
  - `Subject` - Study topics
  - `ConversationSession` - Session tracking
  - `SafetyCheckResult` - Safety check results

### 📥 Document Ingestion (`src/ingestion/`)

- **[src/ingestion/pipeline.py](src/ingestion/pipeline.py)** - Main ingestion orchestrator
  - Coordinates: Parse → Chunk → Embed → Store
  - Error handling and status tracking
  - Integration point for all ingestion steps

- **[src/ingestion/pdf_parser.py](src/ingestion/pdf_parser.py)** - PDF parsing
  - PyMuPDF (primary), Marker (optional), fallback
  - Extracts text while preserving structure
  - Returns markdown text and page count

- **[src/ingestion/chunking.py](src/ingestion/chunking.py)** - Text chunking
  - Character-based splitting (1000 chars, 100 overlap)
  - Injects metadata: source, page number, section
  - Returns list of `Chunk` objects

- **[src/ingestion/embeddings.py](src/ingestion/embeddings.py)** - Embedding generation
  - Calls Ollama's embedding API
  - Uses nomic-embed-text model (768-dimensional vectors)
  - Stores embeddings in ChromaDB with metadata

### 🔍 Retrieval & Ranking (`src/retrieval/`)

- **[src/retrieval/vector_store.py](src/retrieval/vector_store.py)** - ChromaDB integration
  - `get_or_create_collection()` - Get/create ChromaDB collections
  - `add_chunks_with_embeddings()` - Store chunks with embeddings
  - `query_collection()` - Semantic search with vectors
  - `delete_collection()` - Remove collections
  - `list_collections()` - List all collections

- **[src/retrieval/bm25_index.py](src/retrieval/bm25_index.py)** - BM25 keyword search
  - `BM25Index` class for building and searching
  - Uses rank-bm25 library
  - Tokenizes text and indexes for keyword matching
  - Returns chunks ranked by relevance

- **[src/retrieval/hybrid_retriever.py](src/retrieval/hybrid_retriever.py)** - Ensemble retrieval
  - `HybridRetriever` class - Main retriever interface
  - Combines BM25 (30%) + semantic search (70%)
  - Merges and deduplicates results
  - Calls reranker for final ranking

- **[src/retrieval/reranker.py](src/retrieval/reranker.py)** - Cross-encoder reranking
  - Uses bge-reranker-base model
  - Re-orders results by semantic relevance
  - Returns top-N most relevant chunks

### 🧠 Generation & Response (`src/generation/`)

- **[src/generation/rag_chain.py](src/generation/rag_chain.py)** - Main RAG orchestrator
  - `ask_question()` - End-to-end RAG pipeline
  - Coordinates: retrieve → rerank → generate → extract citations
  - Handles conversation history
  - Returns `ChatMessage` with answer and citations

- **[src/generation/llm_client.py](src/generation/llm_client.py)** - Ollama LLM interface
  - `check_ollama_health()` - Verify Ollama is running
  - `get_llm()` - Get cached ChatOllama instance
  - Model: llama3.2 (14B parameters)

- **[src/generation/grounding.py](src/generation/grounding.py)** - Citation extraction
  - `extract_citations()` - Get citations from results
  - `format_citations()` - Format for display
  - `build_context()` - Format context for LLM prompt

### 🛡️ Safety (`src/safety/`)

- **[src/safety/guardrail.py](src/safety/guardrail.py)** - Content safety checking
  - `check_safety()` - Query safety check via llama-guard3
  - Categorizes violations (S1-S14)
  - Hard-block vs. soft-block categories
  - Returns `SafetyCheckResult`

### 🔧 Utilities (`src/utils/`)

- **[src/helpers.py](src/utils/helpers.py)** - Helper functions
  - `slugify()` - Convert text to slug format
  - `sha256_short()` - Hash file for uniqueness
  - `collection_name_for_file()` - Deterministic collection naming
  - `is_pdf()` - Check if file is PDF
  - `validate_file_size()` - File size validation

### 📦 Dependencies

- **[requirements.txt](requirements.txt)** - Python package dependencies
  - Core: streamlit, langchain, pydantic
  - AI: sentence-transformers, rank-bm25
  - Storage: chromadb, pymupdf
  - Utils: httpx, pytest

### 📊 Data Directory Structure

```
data/
├── chromadb/           # ChromaDB persistent vector store
│   └── [collection-specific files]
├── uploads/            # Temporary uploaded PDF files
│   └── [user-uploaded PDFs]
└── curriculum/         # Reference/sample curriculum
    └── [reference materials]
```

### 🧪 Testing

- **[tests/conftest.py](tests/conftest.py)** - Pytest configuration and fixtures
  - Mock Ollama endpoints
  - Sample data fixtures
  - Mock responses for testing

- **[tests/unit/](tests/unit/)** - Unit tests
- **[tests/integration/](tests/integration/)** - Integration tests
- **[tests/contract/](tests/contract/)** - Contract tests

## Key File Relationships

```
app.py (Streamlit UI)
  ├─ calls → src/ingestion/pipeline.py (ingest_document)
  ├─ calls → src/generation/rag_chain.py (ask_question)
  └─ calls → src/generation/llm_client.py (check_ollama_health)

src/ingestion/pipeline.py
  ├─ calls → pdf_parser.py
  ├─ calls → chunking.py
  ├─ calls → embeddings.py
  ├─ calls → bm25_index.py (build index)
  └─ calls → vector_store.py (store embeddings)

src/generation/rag_chain.py
  ├─ calls → safety/guardrail.py (check_safety)
  ├─ calls → retrieval/hybrid_retriever.py (retrieve)
  ├─ calls → generation/llm_client.py (generate)
  └─ calls → generation/grounding.py (extract citations)

src/retrieval/hybrid_retriever.py
  ├─ uses → bm25_index.py (keyword search)
  ├─ uses → vector_store.py (semantic search)
  ├─ uses → embeddings.py (query embeddings)
  └─ uses → reranker.py (reranking)
```

## Configuration Flow

```
.env (environment variables with RUSS_ prefix)
  ↓
src/config/settings.py (Pydantic BaseSettings)
  ├─ Ollama URLs and models
  ├─ Chunk sizes and overlap
  ├─ Retrieval weights
  ├─ File paths
  └─ Other parameters
  
src/config/prompts.py (prompt templates)
  └─ System prompts and response formats
```

## Data Flow

```
PDF Upload
  → parse_pdf() → markdown text
  → chunk_document() → Chunk objects
  → generate_embeddings() → [float] vectors
  → add_chunks_with_embeddings() → ChromaDB
  → bm25_index.build_index() → BM25 Index

User Query
  → check_safety() → SafetyCheckResult
  → HybridRetriever.retrieve() → RetrievalResult[]
  → rerank() → RetrievalResult[] (reranked)
  → build_context() → formatted context
  → llm.invoke() → answer text
  → extract_citations() → Citation[]
  → ChatMessage (answer + citations)
```

## Usage Examples

### Run Validation
```bash
python validate.py
```

### Start Application
```bash
streamlit run app.py
```

### Start Ollama
```bash
ollama serve
```

### Pull Models
```bash
ollama pull llama3.2 nomic-embed-text llama-guard3:1b
```

## Quick Reference

| Task | File |
|------|------|
| Start app | `app.py` |
| Configure | `.env` + `src/config/settings.py` |
| Upload PDF | Streamlit UI → `src/ingestion/pipeline.py` |
| Ask question | Streamlit UI → `src/generation/rag_chain.py` |
| Search | `src/retrieval/hybrid_retriever.py` |
| Check safety | `src/safety/guardrail.py` |
| Validate setup | `validate.py` |

---

**Last Updated:** February 23, 2025

For more details, see [README.md](README.md) and [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
