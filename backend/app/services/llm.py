from __future__ import annotations

import hashlib
import logging
import math
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.services.usage_limits import (
    LLMUsageContext,
    UsageLimitExceeded,
    usage_limit_service,
)

logger = logging.getLogger(__name__)


def _deterministic_embedding(text: str, dim: int = 1536) -> list[float]:
    """Hash-based mock embedding for dev without OPENAI_API_KEY."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    for i in range(dim):
        byte = digest[i % len(digest)]
        values.append((byte / 127.5) - 1.0)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def _default_usage_context() -> LLMUsageContext:
    plan = usage_limit_service.resolve_plan(university_slug=settings.default_university_slug)
    return LLMUsageContext(
        university_id=settings.default_university_slug,
        user_id=None,
        user_role="student",
        plan=plan,
    )


def _stub_completion(prompt: str) -> str:
    return (
        "[LLM stub] Configure OPENAI_API_KEY and an eligible plan to enable real completions. "
        f"Prompt received ({len(prompt)} chars)."
    )


class LLMService:
    """LLM interface — uses OpenAI when allowed by plan limits, otherwise graceful stubs."""

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

    def _resolve_context(self, usage: Optional[LLMUsageContext]) -> LLMUsageContext:
        return usage or _default_usage_context()

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        usage: Optional[LLMUsageContext] = None,
    ) -> str:
        context = self._resolve_context(usage)
        limits = usage_limit_service.get_effective_limits(context.plan, context.user_role)

        if not settings.openai_api_key or limits.daily_llm_calls_university <= 0:
            return _stub_completion(prompt)

        cache_raw = f"{context.plan}:{system or ''}:{prompt}:{temperature}"
        cached = usage_limit_service.cache_get("llm_complete", cache_raw)
        if cached is not None:
            return str(cached)

        effective = usage_limit_service.check_can_make_llm_call(context)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": temperature,
        }
        if effective.max_tokens_per_call > 0:
            payload["max_tokens"] = effective.max_tokens_per_call

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", effective.max_tokens_per_call)
            usage_limit_service.record_llm_usage(context, tokens_used=tokens_used)
            usage_limit_service.cache_set("llm_complete", cache_raw, content)
            return content

    async def embed(
        self,
        text: str,
        usage: Optional[LLMUsageContext] = None,
    ) -> list[float]:
        context = self._resolve_context(usage)
        limits = usage_limit_service.get_effective_limits(context.plan, context.user_role)

        cached = usage_limit_service.cache_get("llm_embed", text)
        if cached is not None:
            return list(cached)

        if not settings.openai_api_key or not limits.real_embeddings_enabled:
            embedding = _deterministic_embedding(text)
            usage_limit_service.cache_set("llm_embed", text, embedding)
            return embedding

        usage_limit_service.check_can_make_llm_call(context)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers=self._headers(),
                json={"model": "text-embedding-3-small", "input": text},
            )
            response.raise_for_status()
            data = response.json()
            embedding = data["data"][0]["embedding"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            usage_limit_service.record_llm_usage(context, tokens_used=tokens_used)
            usage_limit_service.cache_set("llm_embed", text, embedding)
            return embedding

    async def synthesize_answer(
        self,
        query: str,
        context_chunks: list[dict[str, Any]],
        usage: Optional[LLMUsageContext] = None,
    ) -> str:
        if not context_chunks:
            return "No relevant documents found."

        ctx = self._resolve_context(usage)
        limits = usage_limit_service.get_effective_limits(ctx.plan, ctx.user_role)

        if not limits.llm_synthesis_enabled or not settings.openai_api_key:
            top = context_chunks[0]
            return (
                f"Based on official university documents:\n\n{top.get('excerpt', '')}\n\n"
                f"Source: {top.get('document_title', 'Unknown')}"
            )

        context = "\n\n---\n\n".join(
            f"Document: {c.get('document_title', 'Unknown')}\n{c.get('excerpt', '')}"
            for c in context_chunks
        )
        system = (
            "You are the CampusOS Knowledge Agent. Answer using ONLY the provided context. "
            "Always cite document titles. If the context is insufficient, say so."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}"
        try:
            return await self.complete(prompt, system=system, temperature=0.3, usage=ctx)
        except UsageLimitExceeded:
            raise
        except httpx.HTTPError as exc:
            logger.warning("OpenAI synthesis failed: %s", exc)
            top = context_chunks[0]
            return (
                f"Based on official university documents:\n\n{top.get('excerpt', '')}\n\n"
                f"Source: {top.get('document_title', 'Unknown')}"
            )


llm_service = LLMService()
