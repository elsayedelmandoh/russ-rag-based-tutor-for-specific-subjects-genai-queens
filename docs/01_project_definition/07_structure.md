## Project Structure

### Top-Level Layout (Important Files and Folders)

```
russ-rag-based-tutor-for-specific-subjects-genai-queens/
├── app.py                           # Entry point: Streamlit UI for chat + PDF upload
├── requirements.txt                 # Pinned Python dependencies
├── .env                             # Local configuration (API keys, model names, etc.)
├── README.md                        # Project overview and setup instructions
├── data/
│   ├── chromadb/                    # Persistent ChromaDB vector store (local)
│   ├── curriculum/                  # Sample/reference curriculum PDFs
│   └── uploads/                     # Temporary directory for user-uploaded PDFs
├── docs/
│   └── 01_project_definition/       # Architecture, workflow, and stack documentation
│       ├── 00_quickstart.md
│       ├── 01_problem.md
│       ├── 02_goal.md
│       ├── 03_solution.md
│       ├── 04_stack.md
│       ├── 05_architecture.md
│       ├── 06_workflow.md
│       ├── 07_structure.md
│       └── 08_report.md
├── src/                             # Application source code (modular design)
│    ├── config/                     # Settings, environment loading, prompt templates
│    │   ├── prompts.py              # 
│    │   └── settings.py             # 
│    ├── generation/                 # LLM orchestration, RAG chain, grounding, citation
│    │   ├── grounding.py            # 
│    │   ├── llm_client.py           # 
│    │   └── rag_chain.py            # 
│    ├── ingestion/                  # PDF parsing, chunking, embedding generation
│    │   ├── chunking.py             # 
│    │   ├── embeddings.py           # 
│    │   ├── pdf_parser.py           # 
│    │   └── pipeline.py             # 
│    ├── models/                     # Pydantic schemas for type safety
│    │   └── schemas.py              # 
│    ├── retrieval/                  # ChromaDB interface, BM25 indexing, hybrid retrieval
│    │   ├── bm25_index.py           #
│    │   ├── hybrid_retriever.py     #
│    │   ├── reranker.py             #
│    │   └── vector_store.py         #
│    ├── safty/                      #
│    │   └── guardrail.py            # Strict content safety filtering
│    └── utils/                      # Helper functions, validators, data processing
│    │   ├── helpers.py              #
│    │   └── validate.py             #
└── tests/                           # Unit tests and test suites
    ├── __init__.py
    ├── conftest.py
    ├── contract/
    ├── integration/
    ├── results/
    └── unit/
```

### Module Descriptions

#### **config/** - Configuration & Prompts
- `prompts.py` - System prompts and templates for the LLM
- `settings.py` - Environment parsing, model names, API endpoints, chunk sizes
**Purpose:** Centralized configuration; easy switching between models/settings without code changes.

#### **generation/** - LLM & Response Generation
- `grounding.py` - Citation extraction and source attribution
- `llm_client.py` - Ollama API wrapper for model inference
- `rag_chain.py` - Core RAG orchestration (retrieval → re-ranking → generation)
**Purpose:** Manage the full RAG pipeline from query to grounded, cited response.

#### **ingestion/** - Data Ingestion Pipeline
- `chunking.py` - Split text into overlapping chunks with metadata injection
- `embeddings.py` - Generate embeddings using nomic-embed-text via Ollama
- `pdf_parser.py` - Extract text, tables, equations from parsed PDFs
- `pipeline.py` - Document ingestion pipeline orchestrator
**Purpose:** Convert raw PDFs → chunked, embedded, metadata-rich document collection.

#### **models/** - Data Schemas
- `schemas.py` - Pydantic models (Document, Citation, ChatMessage, etc.)
**Purpose:** Type-safe data contracts throughout the application.

#### **retrieval/** - Retrieval & Ranking
- `bm25_index.py` - Build BM25 index from chunked documents
- `hybrid_retriever.py` - Merge BM25 (keyword) + semantic (vector) search results
- `reranker.py` - Cross-encoder reranking for retrieval results
- `vector_store.py` - ChromaDB collection management and initialization
**Purpose:** Implement hybrid search (sparse + dense) + result merging for high-quality context retrieval.

#### **safety/** - Utility Functions
- `guardrail.py` - Content safety filtering using llama-guard3.
**Purpose:** Evaluates the user message for harmful content.

#### **utils/** - Utility Functions
- `helpers.py` - Miscellaneous helpers (file I/O, formatting, etc.)
- `validate.py` - Quick manual validation script to check all imports works.
**Purpose:** Reusable logic and validation logic shared across modules.

#### **tests/** - Unit Tests
- `test_pdf.py` - Test PDF parsing and chunking
- `test_ollama.py` - Test Ollama connectivity and model inference
**Purpose:** Just a dummy test to verify core components in isolation.

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