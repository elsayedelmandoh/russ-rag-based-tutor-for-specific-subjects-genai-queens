from __future__ import annotations

import httpx
import logging
from typing import List

from langchain_ollama import ChatOllama

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Cache LLM instance to avoid recreating
_llm_instance = None


def check_ollama_health(timeout: float = 5.0) -> dict:
    """Call Ollama `/api/tags` and verify required models are available.

    Returns a dict with keys:
      - available: List[str]
      - missing: List[str]
      - ok: bool
    """
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        resp = httpx.get(url, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        models = [m.get("name", "") for m in payload.get("models", [])]

        required = [settings.llm_model, settings.embedding_model, settings.guard_model]

        # Normalize: models in Ollama tag list may be suffixed with :latest
        normalized = [m.split(":")[0] for m in models]

        available: List[str] = [r for r in required if r.split(":")[0] in normalized]
        missing: List[str] = [r for r in required if r.split(":")[0] not in normalized]

        return {"available": available, "missing": missing, "ok": len(missing) == 0}
    except Exception as exc:  # pragma: no cover - network/runtime
        return {"available": [], "missing": [settings.llm_model, settings.embedding_model, settings.guard_model], "ok": False, "error": str(exc)}


def get_llm() -> ChatOllama:
    """Get or create a ChatOllama LLM instance.

    Returns:
        ChatOllama instance configured with settings
    """
    global _llm_instance
    if _llm_instance is None:
        logger.info(f"Creating ChatOllama LLM: {settings.llm_model}")
        _llm_instance = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
        )
    return _llm_instance
