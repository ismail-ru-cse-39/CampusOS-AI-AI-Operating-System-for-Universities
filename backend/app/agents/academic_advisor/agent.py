from app.agents.base import Agent, AgentContext, AgentResult


class AcademicAdvisorAgent(Agent):
    name = "academic_advisor"
    description = "Course planning, degree roadmaps, career pathway recommendations"
    keywords = [
        "advisor", "roadmap", "elective", "pathway", "plan", "recommend course",
        "what should i take", "become", "career path", "ai engineer",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Academic Advisor Agent (coming soon in Phase 3). "
                "I will help with course planning, degree roadmaps, and career pathway recommendations. "
                "For now, please contact your assigned academic advisor."
            ),
            metadata={"status": "stub"},
        )
