from __future__ import annotations

from app.agents.base import Agent, AgentContext, AgentResult
from app.agents.registry import agent_registry
from app.core.memory import DEMO_STUDENT_MEMORY


class Orchestrator:
    """Routes user messages to the best-matching specialized agent."""

    async def route(
        self,
        message: str,
        user_role: str = "student",
        user_id: str | None = None,
    ) -> AgentResult:
        memory = DEMO_STUDENT_MEMORY.to_context()
        context = AgentContext(
            message=message,
            user_role=user_role,
            user_id=user_id,
            memory=memory,
        )

        best_agent: Agent | None = None
        best_score = 0.0

        for agent in agent_registry.all():
            score = agent.can_handle(message, user_role)
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent is None or best_score < 0.1:
            from app.agents.knowledge.agent import KnowledgeAgent

            best_agent = KnowledgeAgent()

        return await best_agent.run(context)
