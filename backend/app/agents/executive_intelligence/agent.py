from app.agents.base import Agent, AgentContext, AgentResult


class ExecutiveIntelligenceAgent(Agent):
    name = "executive_intelligence"
    description = "Institutional KPIs, enrollment trends, and executive dashboards"
    keywords = [
        "executive",
        "dashboard",
        "kpi",
        "metrics",
        "enrollment",
        "forecast",
        "retention rate",
        "institutional",
        "leadership",
        "report",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role == "executive":
            return max(score, 0.15) if score > 0 else 0.0
        return score * 0.4

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            message=(
                "Executive Intelligence Agent (coming soon in Phase 5). "
                "I will surface live enrollment, retention, and department performance metrics "
                "with weekly AI-generated leadership reports."
            ),
            metadata={"status": "stub"},
        )
