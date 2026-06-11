from app.agents.base import Agent, AgentContext, AgentResult


class ResearchAssistantAgent(Agent):
    name = "research_assistant"
    description = "Literature discovery, grant matching, research trends, citation assistance"
    keywords = [
        "research", "literature", "grant", "publication", "citation", "paper",
        "proposal", "thesis", "dissertation",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role in ("faculty", "student"):
            return score
        return score * 0.5

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Research Assistant Agent (coming soon in Phase 5). "
                "I will support literature discovery, grant opportunity matching, "
                "research trend analysis, and citation assistance."
            ),
            metadata={"status": "stub"},
        )
