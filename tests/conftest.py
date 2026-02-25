"""Shared pytest fixtures and Ollama mock helpers."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_ollama_chat():
    """Mock Ollama /api/chat endpoint responses."""
    with patch("httpx.Client") as mock_client_cls:
        client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "Mock response."},
            "done": True,
        }
        client.post.return_value = response
        yield client


@pytest.fixture
def mock_ollama_embed():
    """Mock Ollama /api/embed endpoint responses."""
    with patch("httpx.Client") as mock_client_cls:
        client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "model": "nomic-embed-text",
            "embeddings": [[0.1] * 768],
        }
        client.post.return_value = response
        yield client


@pytest.fixture
def mock_ollama_tags():
    """Mock Ollama /api/tags endpoint for health check."""
    with patch("httpx.get") as mock_get:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest", "size": 2000000000},
                {"name": "nomic-embed-text:latest", "size": 274000000},
                {"name": "llama-guard3:1b", "size": 1600000000},
            ]
        }
        mock_get.return_value = response
        yield mock_get


@pytest.fixture
def mock_ollama_guard_safe():
    """Mock Ollama guard response - safe."""
    with patch("httpx.post") as mock_post:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "model": "llama-guard3:1b",
            "message": {"role": "assistant", "content": "safe"},
            "done": True,
        }
        mock_post.return_value = response
        yield mock_post


@pytest.fixture
def mock_ollama_guard_unsafe():
    """Mock Ollama guard response - unsafe."""
    with patch("httpx.post") as mock_post:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "model": "llama-guard3:1b",
            "message": {"role": "assistant", "content": "unsafe\nS1,S10"},
            "done": True,
        }
        mock_post.return_value = response
        yield mock_post


@pytest.fixture
def sample_chunks():
    """Create sample Chunk objects for testing."""
    from src.models.schemas import Chunk

    return [
        Chunk(
            chunk_id="chunk-001",
            text="Radar systems operate by emitting radio waves.",
            source_document="Radar_Vol1.pdf",
            page_number=1,
            section_heading="Introduction",
            chunk_index=0,
            collection_name="radar-vol1-a1b2c3d4",
        ),
        Chunk(
            chunk_id="chunk-002",
            text="Signal processing involves filtering and amplification.",
            source_document="Radar_Vol1.pdf",
            page_number=5,
            section_heading="Signal Processing",
            chunk_index=1,
            collection_name="radar-vol1-a1b2c3d4",
        ),
    ]
