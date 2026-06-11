from app.agents.base import Agent, AgentContext, AgentResult
from app.services.analytics import analytics_service


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
        metrics = analytics_service.get_executive_metrics()
        report = analytics_service.generate_weekly_report()

        msg = (
            f"Executive summary:\n"
            f"  Retention: {metrics['retention_rate']['value']}{metrics['retention_rate']['unit']}\n"
            f"  Enrollment forecast: {metrics['enrollment_forecast']['value']:,} students\n"
            f"  At-risk students: {metrics['at_risk_students']['value']}\n"
            f"  Student satisfaction: {metrics['student_satisfaction']['value']}{metrics['student_satisfaction']['unit']}\n\n"
            f"{report['summary']}"
        )

        return AgentResult(
            agent=self.name,
            message=msg,
            metadata={"metrics": metrics, "report_preview": report["highlights"]},
        )
