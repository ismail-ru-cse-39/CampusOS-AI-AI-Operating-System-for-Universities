from app.agents.base import Agent, AgentContext, AgentResult


class AdmissionsAgent(Agent):
    name = "admissions"
    description = "Prospective student inquiries — programs, requirements, tuition, visa guidance"
    keywords = [
        "admission", "apply", "tuition", "prospect", "international student",
        "program", "entry requirement", "visa", "enroll",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role == "admissions":
            score = max(score, 0.5)
        return score

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Admissions Agent (coming soon in Phase 4). "
                "Available 24/7 for program recommendations, admission requirements, "
                "tuition information, and visa guidance."
            ),
            metadata={"status": "stub"},
        )
