from app.agents.base import Agent, AgentContext, AgentResult
from app.services.notifications import notification_service
from app.services.retention import retention_service


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
        critical = retention_service.at_risk_students("high")
        lines = [f"Retention analysis: {len(critical)} students at high/critical risk."]

        for student in critical[:3]:
            lines.append(
                f"  • {student.student_name}: {student.risk_level} (score {student.score}) — "
                f"{', '.join(student.signals[:2])}"
            )
            await notification_service.notify_at_risk_alert(
                student.student_name, advisor_id="advisor-001"
            )

        if "engineering" in context.message.lower():
            lines.append("\nEngineering department retention: 85.2% (below campus average).")

        lines.append(
            "\nRecommended interventions: advisor outreach, tutoring, financial aid review."
        )

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={
                "at_risk_count": len(critical),
                "alerts_sent": min(3, len(critical)),
            },
        )
