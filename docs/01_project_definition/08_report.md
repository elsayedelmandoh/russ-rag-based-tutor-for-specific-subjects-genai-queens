
# Project Report — RUSS (RAG-Based Tutor)

**Project overview:**
- **RUSS** is a private, offline Retrieval-Augmented Generation tutor that ingests course PDFs and answers student questions with citation-backed responses. The system runs locally (no cloud data leakage) and scopes answers to user-provided subject materials.

**Dataset summary:**
- No external dataset: the system uses uploaded course materials (PDFs) supplied by instructors or students. Documents are parsed, chunked, embedded, and stored locally for query-time retrieval.

**Models & tools:**
- **LLM / Generator:** `llama3.2` (via Ollama)
- **Embeddings:** `nomic-embed-text`
- **Safety / Guardrails:** `llama-guard3:1b`
- **Vector DB:** ChromaDB
- **Keyword search:** `rank_bm25` (BM25)
- **Reranker:** `bge-reranker-base` (cross-encoder)
- **Orchestration:** LangChain
- **PDF parsing:** PyMuPDF (Marker)
- **Frontend:** Streamlit

**Steps to run the demo:**
1. Install deps:
```bash
pip install -r requirements.txt
```
2. Start Ollama in a separate terminal:
```bash
ollama serve
```
3. Pull required models (one-time):
```bash
ollama pull llama3.2 nomic-embed-text llama-guard3:1b
```
4. Run the app:
```bash
streamlit run app.py
```

**Source code:**
- [github](https://github.com/elsayedelmandoh/russ-rag-based-tutor-for-specific-subjects-genai-queens)

**Demo video:**
- [drive]()

---
