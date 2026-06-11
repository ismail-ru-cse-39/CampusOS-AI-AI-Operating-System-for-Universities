from app.agents.base import Agent, AgentContext, AgentResult


class CampusNavigationAgent(Agent):
    name = "campus_navigation"
    description = "Building directions, room locations, walking time estimates"
    keywords = [
        "where is", "building", "room", "directions", "walk", "campus", "library",
        "engineering", "location", "how long",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Campus Navigation Agent (coming soon in Phase 4). "
                "I will provide building directions, room locations, and walking time estimates."
            ),
            metadata={"status": "stub"},
        )
