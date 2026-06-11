from app.agents.base import Agent, AgentContext, AgentResult


class TimetableAgent(Agent):
    name = "timetable"
    description = "Personalized schedule generation with conflict and preference optimization"
    keywords = [
        "timetable", "schedule", "class time", "no friday", "conflict", "gap",
        "morning", "afternoon", "building",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Timetable Agent (coming soon in Phase 4). "
                "I will generate optimized schedules based on your preferences and constraints."
            ),
            metadata={"status": "stub"},
        )
