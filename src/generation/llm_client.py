from __future__ import annotations

import httpx
from typing import List

from src.config.settings import settings


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
