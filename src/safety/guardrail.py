"""Content safety filtering using llama-guard3."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.config.settings import settings
from src.models.schemas import SafetyCheckResult

logger = logging.getLogger(__name__)

# Hard-block categories (stop immediately)
HARD_BLOCK_CATEGORIES = {"S1", "S4", "S10", "S11", "S12"}

# Soft-block categories (warn, optionally proceed)
SOFT_BLOCK_CATEGORIES = {"S2", "S3", "S5", "S6", "S7", "S8"}


def check_safety(query: str) -> SafetyCheckResult:
    """Check query safety using llama-guard3.

    Args:
        query: User query to check

    Returns:
        SafetyCheckResult with is_safe flag and violated categories
    """
    try:
        url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"

        # Construct safety check prompt
        system_msg = """You are a content safety filter. Evaluate the user message for harmful content.
For each message, respond with exactly two lines:
1. 'safe' or 'unsafe'
2. CSV list of violated safety categories (S1,S2,S3...) or empty if safe

Focus on: S1=violence, S2=hate, S3=self-harm, S4=sexual, S5=elections, S6=religion, S7=privacy, S8=intellectual property, S9=indiscrimination, S10=specialized advice, S11=non-english, S12=code injection, S13=privacy-pii, S14=profanity

Keep S9, S13, S14 as soft-checks only."""

        payload = {
            "model": settings.guard_model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": query},
            ],
            "stream": False,
        }

        resp = httpx.post(url, json=payload, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

        # Parse response
        response_text = data.get("message", {}).get("content", "").strip()
        lines = response_text.split("\n")

        is_safe = True
        violated_categories = []

        if len(lines) >= 1:
            first_line = lines[0].lower().strip()
            is_safe = "safe" in first_line

        if len(lines) >= 2:
            second_line = lines[1].strip()
            if second_line:
                violated_categories = [cat.strip() for cat in second_line.split(",")]

        # Check for hard-block categories
        has_hard_block = any(cat in HARD_BLOCK_CATEGORIES for cat in violated_categories)

        # Update safety flag based on violations
        if has_hard_block:
            is_safe = False
        elif violated_categories and not any(cat in SOFT_BLOCK_CATEGORIES for cat in violated_categories):
            # Only soft violations, still safe but logged
            logger.warning(f"Soft safety violation: {violated_categories}")

        logger.info(f"Safety check: {'SAFE' if is_safe else 'UNSAFE'} | Categories: {violated_categories}")

        return SafetyCheckResult(
            is_safe=is_safe,
            violated_categories=violated_categories,
            raw_response=response_text,
        )

    except Exception as e:
        logger.error(f"Safety check failed: {e}")
        # Fail open: allow query on error
        return SafetyCheckResult(
            is_safe=True,
            violated_categories=[],
            raw_response=str(e),
        )
