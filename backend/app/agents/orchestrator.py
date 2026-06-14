from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import Agent, AgentContext, AgentResult
from app.agents.registry import agent_registry
from app.core.config import settings
from app.core.rbac import can_access_agent, parse_role
from app.services.i18n import i18n_service
from app.services.memory import load_student_memory
from app.services.usage_limits import usage_limit_service


class Orchestrator:
    """Routes user messages to the best-matching specialized agent with RBAC."""

    async def route(
        self,
        message: str,
        user_role: str = "student",
        user_id: str | None = None,
        db: Optional[AsyncSession] = None,
        language: str | None = None,
        university_id: str | None = None,
        plan: str | None = None,
    ) -> AgentResult:
        role = parse_role(user_role)
        uid: UUID | None = None
        if user_id:
            try:
                uid = UUID(user_id)
            except ValueError:
                uid = None

        memory = await load_student_memory(db, uid)
        lang = language or i18n_service.detect_language(message)

        uni_id = university_id or settings.default_university_slug
        resolved_plan = usage_limit_service.resolve_plan(plan=plan, university_slug=uni_id)

        context = AgentContext(
            message=message,
            user_role=user_role,
            user_id=user_id,
            university_id=uni_id,
            plan=resolved_plan,
            memory=memory,
        )

        best_agent: Agent | None = None
        best_score = 0.0

        for agent in agent_registry.all():
            if not can_access_agent(role, agent.name):
                continue
            score = agent.can_handle(message, user_role)
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent is None or best_score < 0.1:
            from app.agents.knowledge.agent import KnowledgeAgent

            if can_access_agent(role, "knowledge"):
                best_agent = KnowledgeAgent()
            else:
                return AgentResult(
                    agent="orchestrator",
                    message="You do not have permission to access any agent for this query.",
                    metadata={"status": "forbidden"},
                )

        result = await best_agent.run(context)
        if lang != "en":
            result.message = i18n_service.translate_response(result.message, lang)
            result.metadata["language"] = lang
        return result
