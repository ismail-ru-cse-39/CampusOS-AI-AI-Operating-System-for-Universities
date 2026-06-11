from app.agents.base import Agent, AgentContext, AgentResult


class FacultyIntelligenceAgent(Agent):
    name = "faculty_intelligence"
    description = "At-risk student identification, attendance analysis, course analytics"
    keywords = [
        "at-risk", "attendance", "engagement", "performance", "analytics",
        "intervention", "report", "roster", "student performance",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role in ("faculty", "executive"):
            score = max(score, 0.3 if score > 0 else 0.0)
        return score

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Faculty Intelligence Agent (coming soon in Phase 5). "
                "I will identify at-risk students, analyze attendance and engagement, "
                "and generate course performance reports with intervention recommendations."
            ),
            metadata={"status": "stub"},
        )
