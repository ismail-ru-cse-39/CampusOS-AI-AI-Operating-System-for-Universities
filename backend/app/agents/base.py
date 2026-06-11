from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.schemas import Citation


@dataclass
class AgentContext:
    message: str
    user_role: str
    user_id: str | None = None
    memory: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent: str
    message: str
    citations: list[Citation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    name: str
    description: str
    keywords: list[str] = []

    @abstractmethod
    def can_handle(self, message: str, user_role: str) -> float:
        """Return confidence score 0.0–1.0 for handling this message."""
        ...

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        ...

    def _keyword_score(self, message: str) -> float:
        lower = message.lower()
        matches = sum(1 for kw in self.keywords if kw in lower)
        if not self.keywords:
            return 0.0
        return min(1.0, matches / max(1, len(self.keywords) * 0.5))
