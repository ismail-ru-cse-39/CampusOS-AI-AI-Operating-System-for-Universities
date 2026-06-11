from __future__ import annotations

from typing import Any

from app.core.config import settings


class LLMService:
    """LLM interface — stubbed in Phase 0, wired in Phase 2."""

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
        # Phase 2: integrate OpenAI/Anthropic client
        raise NotImplementedError("LLM integration planned for Phase 2")

    async def embed(self, text: str) -> list[float]:
        # Phase 2: return real embeddings for pgvector
        return [0.0] * 1536


llm_service = LLMService()
