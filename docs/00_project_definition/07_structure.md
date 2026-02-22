## Project Structure

### Top-Level Layout (Important Files and Folders)

```
russ-rag-based-tutor-for-specific-subjects-genai-queens/
├── app.py                          # Entry point: Streamlit UI for chat + PDF upload
├── requirements.txt                # Pinned Python dependencies
├── .env                            # Local configuration (API keys, model names, etc.)
├── README.md                       # Project overview and setup instructions
├── data/
│   ├── chromadb/                   # Persistent ChromaDB vector store (local)
│   ├── curriculum/                 # Sample/reference curriculum PDFs
│   └── uploads/                    # Temporary directory for user-uploaded PDFs
├── docs/
│   └── 00_project_definition/      # Architecture, workflow, and stack documentation
└── src/                            # Application source code (modular design)
    ├── config/                     # Settings, environment loading, prompt templates
    ├── ingestion/                  # PDF parsing, chunking, embedding generation
    ├── retrieval/                  # ChromaDB interface, BM25 indexing, hybrid retrieval
    ├── generation/                 # LLM orchestration, RAG chain, grounding, citation
    ├── models/                     # Pydantic schemas for type safety
    └── utils/                      # Helper functions, validators, data processing
└── tests/                          # Unit tests for PDF parsing, Ollama integration
```

### Module Descriptions

#### **config/** - Configuration & Prompts
- `settings.py` - Environment parsing, model names, API endpoints, chunk sizes
- `prompts.py` - System prompts and templates for the LLM
- `prompt_strict.py` - Strict/guardrailed prompt variants (optional)

**Purpose:** Centralized configuration; easy switching between models/settings without code changes.

---

#### **ingestion/** - Data Ingestion Pipeline
- `pdf_loader.py` - Load and parse PDF files using Marker + PyMuPDF
- `pdf_parser.py` - Extract text, tables, equations from parsed PDFs
- `chunking.py` - Split text into overlapping chunks with metadata injection
- `embeddings.py` - Generate embeddings using nomic-embed-text via Ollama
- `langchain_splitter.py` - Optional LangChain text splitting integration

**Purpose:** Convert raw PDFs → chunked, embedded, metadata-rich document collection.

---

#### **retrieval/** - Retrieval & Ranking
- `vector_store.py` - ChromaDB collection management and initialization
- `build_hybrid.py` - Build BM25 index from chunked documents
- `hybrid_retriever.py` - Merge BM25 (keyword) + semantic (vector) search results
- `langchain_ensemble.py` - LangChain EnsembleRetriever integration

**Purpose:** Implement hybrid search (sparse + dense) + result merging for high-quality context retrieval.

---

#### **generation/** - LLM & Response Generation
- `llm_interface.py` - Ollama API wrapper for model inference
- `rag_chain.py` - Core RAG orchestration (retrieval → re-ranking → generation)
- `rag_chain_lc.py` - LangChain-based RAG chain (optional alternative)
- `grounding.py` - Citation extraction and source attribution

**Purpose:** Manage the full RAG pipeline from query to grounded, cited response.

---

#### **models/** - Data Schemas
- `schemas.py` - Pydantic models (Document, Citation, ChatMessage, etc.)

**Purpose:** Type-safe data contracts throughout the application.

---

#### **utils/** - Utility Functions
- `helpers.py` - Miscellaneous helpers (file I/O, formatting, etc.)
- `validators.py` - Input validation (file types, query sanity, etc.)

**Purpose:** Reusable logic and validation logic shared across modules.

---

#### **tests/** - Unit Tests
- `test_pdf.py` - Test PDF parsing and chunking
- `test_ollama.py` - Test Ollama connectivity and model inference

**Purpose:** Verify core components work correctly in isolation.

---

### Data Flow Through Modules

```
User Upload (app.py)
    → ingestion/pdf_loader + pdf_parser
    → ingestion/chunking (+ metadata)
    → ingestion/embeddings
    ↓
    ├─ retrieval/vector_store (ChromaDB)
    └─ retrieval/build_hybrid (BM25 index)

User Query (app.py)
    → retrieval/hybrid_retriever
    → [re-ranker: bge-reranker-base]
    → generation/rag_chain
    → generation/grounding
    ↓
    [Citation + Answer] → app.py → Streamlit UI
```

### Key Design Principles

1. **Modularity:** Each module has a single responsibility
2. **Configuration-Driven:** Prompts, models, hyperparameters in `config/`
3. **Type Safety:** Pydantic schemas ensure correctness
4. **Local-First:** All data stored locally; no external API calls (except Ollama)
5. **Metadata Preservation:** Every chunk retains source/page/section info for grounding