from __future__ import annotations

import hashlib
import math
from typing import Any

from app.core.config import settings


def _deterministic_embedding(text: str, dim: int = 1536) -> list[float]:
    """Hash-based mock embedding for dev without OPENAI_API_KEY."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    for i in range(dim):
        byte = digest[i % len(digest)]
        values.append((byte / 127.5) - 1.0)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


class LLMService:
    """LLM interface with graceful fallback when API key is absent."""

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        if not settings.openai_api_key:
            return (
                "[LLM stub] Configure OPENAI_API_KEY to enable real completions. "
                f"Prompt received ({len(prompt)} chars)."
            )
        raise NotImplementedError("Wire OpenAI client when OPENAI_API_KEY is configured")

    async def embed(self, text: str) -> list[float]:
        if settings.openai_api_key:
            raise NotImplementedError("Wire OpenAI embeddings when OPENAI_API_KEY is configured")
        return _deterministic_embedding(text)

    async def synthesize_answer(self, query: str, context_chunks: list[dict[str, Any]]) -> str:
        if not context_chunks:
            return "No relevant documents found."
        if not settings.openai_api_key:
            top = context_chunks[0]
            return (
                f"Based on official university documents:\n\n{top.get('excerpt', '')}\n\n"
                f"Source: {top.get('document_title', 'Unknown')}"
            )
        raise NotImplementedError("Wire OpenAI completions when OPENAI_API_KEY is configured")


llm_service = LLMService()
