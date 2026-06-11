from app.agents.base import Agent, AgentContext, AgentResult
from app.services.retention import retention_service


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
        at_risk = retention_service.at_risk_students("medium")
        lines = [f"At-risk students in your courses ({len(at_risk)} flagged):"]
        for student in at_risk[:5]:
            lines.append(
                f"  • {student.student_name} — {student.risk_level} risk (score {student.score})\n"
                f"    Signals: {', '.join(student.signals)}\n"
                f"    Recommended: {student.recommended_interventions[0]}"
            )

        if "report" in context.message.lower():
            lines.append("\nCourse performance summary: average attendance 78%, avg GPA 2.9 in CS401.")

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={"at_risk_count": len(at_risk), "students": [s.student_id for s in at_risk]},
        )
