from app.agents.base import Agent, AgentContext, AgentResult


class CareerAgent(Agent):
    name = "career"
    description = "Internship matching, job recommendations, resume guidance, career pathways"
    keywords = [
        "internship", "job", "career", "resume", "cv", "employer", "placement",
        "industry", "opportunity",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        interests = context.memory.get("career_interests", [])
        return AgentResult(
            agent=self.name,
            message=(
                f"Career Agent (coming soon in Phase 4). "
                f"Based on your interests ({', '.join(interests) or 'not set'}), "
                "I will recommend internships, jobs, and career pathways."
            ),
            metadata={"status": "stub", "career_interests": interests},
        )
