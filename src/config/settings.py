from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
	"""Application settings loaded from environment variables prefixed with RUSS_.

	Uses Pydantic v2 `SettingsConfigDict` to set `env_file` and `env_prefix`.
	"""

	model_config = SettingsConfigDict(env_file=".env", env_prefix="RUSS_")

	# Ollama / LLM models
	ollama_base_url: str = Field("http://localhost:11434", description="Base URL for Ollama API")
	llm_model: str = Field("llama3.2", description="LLM model name for chat generations")
	embedding_model: str = Field("nomic-embed-text", description="Embedding model name used for vectorization")
	guard_model: str = Field("llama-guard3:1b", description="Safety guard model name")
	reranker_model: str = Field("BAAI/bge-reranker-base", description="Cross-encoder reranker model")

	# Chunking
	chunk_size: int = Field(1000, description="Chunk size in characters")
	chunk_overlap: int = Field(100, description="Chunk overlap in characters")

	# Retrieval weights and params
	semantic_weight: float = Field(0.7, description="Weight for semantic retrieval in hybrid retriever")
	bm25_weight: float = Field(0.3, description="Weight for BM25 retrieval in hybrid retriever")
	retrieval_k: int = Field(20, description="Number of candidates retrieved from each retriever")
	rerank_top_n: int = Field(5, description="Number of top results to rerank with the cross-encoder")

	# Paths
	chromadb_path: str = Field("./data/chromadb", description="Path for ChromaDB persistence")
	uploads_path: str = Field("./data/uploads", description="Path to store uploaded files")

	# PDF parsing
	pdf_parser: str = Field("pymupdf", description="Primary PDF parser: marker or pymupdf")
	max_file_size_mb: int = Field(100, description="Maximum allowed upload file size in megabytes")


settings = Settings()
