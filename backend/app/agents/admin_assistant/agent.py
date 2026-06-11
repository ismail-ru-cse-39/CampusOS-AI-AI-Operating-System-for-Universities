from app.agents.base import Agent, AgentContext, AgentResult


class AdminAssistantAgent(Agent):
    name = "admin_assistant"
    description = "Automate university services — transcripts, enrollment verification, appointments"
    keywords = [
        "transcript", "verification", "appointment", "book", "submit", "form",
        "request", "status", "document request",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role in ("admin", "student"):
            return score
        return score * 0.5

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Administrative Assistant Agent (coming soon in Phase 4). "
                "I will execute workflows for transcript requests, enrollment verification, "
                "appointment booking, and form submissions."
            ),
            metadata={"status": "stub"},
        )
