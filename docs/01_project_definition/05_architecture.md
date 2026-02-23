## Architecture

### Data Ingestion Pipeline

```
User Upload PDF(s)
    ↓
[PDF Parser: Marker + PyMuPDF]
    ├─ Extracts text, tables, LaTeX equations
    └─ Preserves formatting and structure
    ↓
[Text Splitting: RecursiveCharacterTextSplitter]
    ├─ 1000 tokens per chunk
    ├─ 100 token overlap
    └─ Inject metadata: source_file, page_number, section
    ↓
[Embeddings: nomic-embed-text (via Ollama)]
    └─ Dense numerical vectors for semantic search
    ↓
[Storage]:
    ├─ ChromaDB (local, persistent vector database)
    └─ BM25 Index (keyword-based inverted index)
```

### Retrieval & Ranking Pipeline

```
User Query
    ↓
[Hybrid Retriever: EnsembleRetriever]
    ├─ Semantic Search: ChromaDB (weight: 0.7)
    ├─ Keyword Search: BM25 (weight: 0.3)
    └─ Merge & deduplicate results
    ↓
[Re-ranker: bge-reranker-base]
    └─ Cross-encoder re-orders top results by relevance
    ↓
[Guardrails: llama-guard3]
    └─ Safety check ensuring educational boundaries
    ↓
Top-K chunks + metadata ready for generation
```

### Generation & Response Pipeline

```
Retrieved Context + User Query
    ↓
[LLM: Ollama llama3.2]
    ├─ System prompt enforces source-only responses
    ├─ Chain-of-Thought reasoning (if enabled)
    └─ Generates answer grounded in retrieved context
    ↓
[Citation Grounding]
    ├─ Extract exact source file, page number, quote
    └─ Format citations with metadata
    ↓
User sees:
    ├─ Generated answer
    ├─ 📖 Sources footer (page numbers + snippets)
    └─ Optional: reasoning trace (CoT)   
```

### Project Sketch

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                 │
│  - Subject management                                    │
│  - PDF upload interface                                  │
│  - Chat interface                                        │
│  - Document status tracking                              │
└──────────────────┬──────────────────────────────────────┘
                   │
       ┌───────────┴──────────────┐
       ▼                          ▼
┌──────────────────┐     ┌────────────────┐
│   INGESTION      │     │  GENERATION    │
│  (PDF → Chunks)  │     │ (Query → Ans)  │
├──────────────────┤     ├────────────────┤
│ pdf_parser.py    │     │ rag_chain.py   │
│ chunking.py      │     │ llm_client.py  │
│ embeddings.py    │     │ grounding.py   │
│ pipeline.py      │     │ guardrail.py   │
└────────┬─────────┘     └──────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
              ┌─────▼──────┐
              │ RETRIEVAL  │
              ├────────────┤
              │ ChromaDB   │
              │ BM25 Index │
              │ Reranker   │
              └────────────┘
```