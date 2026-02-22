# RUSS: RAG-Based Tutor for Specific Subjects

## Short Description

RUSS is a localized Retrieval-Augmented Generation (RAG) system designed as a "Private NotebookLM" for cadets at the Air Defense College. It ingests complex technical manuals (PDFs) into a secure vector store and allows students to query them using natural language.

**Limitations:** Text and tables only (no image analysis); strictly air-gapped (no internet access).

## What Will You Achieve?

**Learn:**
- Master end-to-end RAG pipeline implementation using Langchain
- Implement Hybrid Search (sparse keyword + dense semantic search) for military terminology
- Deploy local LLMs (Llama 3 or Mistral) using Ollama

**Produce:**
- Functional local web interface (Streamlit) for PDF upload and citation-backed answers
- Llama 3 model running entirely offline

**Prior Knowledge:** Python proficiency, API structures, basic LLM text processing

## Why This Project?

RUSS solves the "Pain of Secrecy" in military education. Cadets need modern AI assistance for engineering concepts but cannot use cloud tools like ChatGPT. RUSS provides a secure, intelligent tutor within isolated networks while ensuring data sovereignty.

## Final Deliverable & Users

**Deliverable:** Python RAG application with Streamlit frontend trained on engineering subjects. Key feature: **Source Verification Footer** displaying exact page numbers and text snippets to prevent hallucinations.

**Target Users:** Cadets and instructors at the Egyptian Air Defense College (expandable to broader Military Academy branches).

## Project Scope (30 Hours)

**Included:**
- Smart PDF parsing (Marker/PyMuPDF) preserving equations and tables
- Local embeddings storage (ChromaDB)
- Hybrid Retriever (BM25 + vector similarity)
- Llama 3 (8B-Instruct) via Ollama as the reasoning engine.
- Strict prompt engineering with citations
- Simple Streamlit chat interface

**Excluded:**
- Multi-modal RAG (image/diagram analysis)
- Model fine-tuning
- Academy grading system integration
- Chat history persistence