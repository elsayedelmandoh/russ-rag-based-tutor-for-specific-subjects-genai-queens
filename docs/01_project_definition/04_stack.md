# Local RAG Tutor: Architecture Stack

This document outlines the specific technologies and tools used to build the **Local RAG Tutor**. The system is designed to operate entirely locally to ensure data privacy, high academic retrieval accuracy, and total security during use.


## 1. Core Language Models (via Ollama)

* **Generator (LLM):** `llama3.2`

    * *Role:* The reasoning engine. We implement **Chain-of-Thought (CoT)** prompting here, forcing the model to "think" through the academic context before generating the final student response.

    * **Command:** `ollama run llama3.2`


* **Embedder:** `nomic-embed-text`

    * *Role:* Converts parsed text into dense numerical vectors for semantic search.

    * **Command:** `ollama pull nomic-embed-text`


* **Guardrails:** `llama-guard3`

    * *Role:* A safety filter to ensure all interactions remain within educational boundaries.

    * **Command:** `ollama pull llama-guard3`



## 2. Data Ingestion & Processing

* **PDF Parsing:** `Marker`

    * *Role:* High-fidelity extraction of text, tables, and LaTeX formulas.

* **Text Splitting & Metadata Injection:** `RecursiveCharacterTextSplitter`

    * *Enhancement:* Every chunk is tagged with **Metadata** (e.g., `source_file`, `page_number`, `lecture_title`). This is critical for the **Self-Citation** feature, allowing the tutor to tell the student exactly where to find the info in their slides.


## 3. Storage & Retrieval (Hybrid Approach)

* **Vector Database (Semantic Search):** `ChromaDB`

  * *Role:* A local database that stores embeddings and manages searching for concepts and meanings similar to the student's question.

* **Keyword Search (Exact Match):** `rank_bm25`

  * *Role:* A keyword-matching algorithm essential for finding specific academic terms, acronyms, or proper names of laws/theories.

* **Hybrid Orchestrator:** `EnsembleRetriever` (via LangChain)

  * *Role:* The orchestrator that merges results from `ChromaDB` (contextual understanding) and `rank_bm25` (literal matching) to ensure the highest possible retrieval accuracy.

* **Re-ranker (The Accuracy Booster):** `bge-reranker-base`

    * *Role:* A cross-encoder model that takes the top results from the hybrid search and re-orders them based on exact relevance to the query. This ensures the "Generator" only sees the most pertinent academic data.


## 4. Application Logic & UI

* **Orchestration:** `LangChain`

    * *Role:* Manages the complex flow between the retriever, re-ranker, and the LLM. It enforces strict "Source-only" responses.

* **Frontend / User Interface:** `Streamlit`

    * *Role:* A clean interface that displays the chat history, thought process (CoT), and clickable source citations.

## Technology Stack Summary

| Layer              | Technology         |
| **UI**             | Streamlit 1.28+    |
| **LLM**            | Ollama + llama3.2  |
| **Embeddings**     | nomic-embed-text   |
| **Vector DB**      | ChromaDB           |
| **Keyword Search** | BM25 (rank-bm25)   |
| **Reranking**      | bge-reranker-base  |
| **Safety**         | llama-guard3:1b    |
| **PDF Parsing**    | PyMuPDF            |
| **Framework**      | LangChain, Pydantic|
| **Language**       | Python 3.11        |