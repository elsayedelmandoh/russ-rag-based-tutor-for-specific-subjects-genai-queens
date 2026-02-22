## Workflow

### Document Ingestion (PDF Upload)

1. User opens `app.py` (Streamlit) and uploads one or more curriculum PDFs
2. System parses PDFs using **Marker** + **PyMuPDF**:
   - Extracts text, tables, and LaTeX equations
   - Preserves page numbers and structure
3. Text splitting via **RecursiveCharacterTextSplitter**:
   - Creates chunks of ~1000 tokens with 100-token overlap
   - Attaches metadata: `source_file`, `page_number`, `section_title`
4. Embeddings generated via **nomic-embed-text** (Ollama)
5. Storage in two structures:
   - **ChromaDB collection** (one per PDF source) for semantic search
   - **BM25 Index** for keyword-based retrieval
6. Collections persist on disk (`data/chromadb/`) for future sessions

### Query & Retrieval (User Asks a Question)

7. User types a question in the chat UI
8. **Hybrid Retriever** (EnsembleRetriever) fetches results:
   - Semantic search from ChromaDB (0.7 weight)
   - Keyword search from BM25 (0.3 weight)
   - Merges and deduplicates results
9. **Re-ranker** (bge-reranker-base) re-orders top-K results:
   - Cross-encoder model refines relevance ranking
   - Ensures only highest-quality chunks reach the LLM
10. **Guardrails** (llama-guard3) performs safety check:
    - Ensures query and context remain within educational scope
    - Blocks potentially harmful requests

### Generation & Grounding (LLM Response)

11. **LLM** (Ollama llama3.2) receives:
    - System prompt enforcing source-only, grounded responses
    - Top-K retrieved chunks with full metadata
    - User's question as context
12. LLM generates answer with Chain-of-Thought reasoning (optional)
13. **Citation Grounding** post-processes the response:
    - Extracts exact source file, page number, text snippet
    - Formats structured citation metadata
14. **UI renders** the final response:
    - Answer text
    - "📖 Sources" footer with page references and snippets
    - Thought trace (if enabled)

### Maintenance Operations

- **Re-indexing:** Clears and re-populates ChromaDB collections for updated materials
- **Persistence:** Collections stored on disk for seamless continuation between runs
- **Per-source isolation:** Each PDF gets its own ChromaDB collection to maintain clear source attribution
