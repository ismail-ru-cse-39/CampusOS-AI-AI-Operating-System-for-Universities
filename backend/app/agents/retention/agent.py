from app.agents.base import Agent, AgentContext, AgentResult


class RetentionAgent(Agent):
    name = "retention"
    description = "Predict student risk and generate early warning alerts"
    keywords = [
        "retention", "dropout", "risk", "early warning", "decline", "churn",
        "predict", "at risk student",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role in ("faculty", "executive", "admin"):
            return score
        return score * 0.3

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Student Retention Agent (coming soon in Phase 5). "
                "I will predict dropout risk from attendance, performance, and engagement signals "
                "and generate early warning alerts with recommended interventions."
            ),
            metadata={"status": "stub"},
        )
