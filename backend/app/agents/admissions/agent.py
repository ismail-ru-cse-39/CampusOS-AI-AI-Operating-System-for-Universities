from app.agents.base import Agent, AgentContext, AgentResult
from app.services.demo_data import ADMISSIONS_PROGRAMS


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
        lower = context.message.lower()
        matched = ADMISSIONS_PROGRAMS

        if "engineering" in lower or "computer" in lower or "data science" in lower:
            matched = [
                p for p in ADMISSIONS_PROGRAMS
                if "engineering" in p["department"].lower()
                or "computer" in p["name"].lower()
                or "data science" in p["name"].lower()
            ] or ADMISSIONS_PROGRAMS

        if "international" in lower or "visa" in lower:
            return AgentResult(
                agent=self.name,
                message=(
                    "International applicants: submit transcripts, English proficiency (IELTS 6.5+), "
                    "and passport copy. F-1 visa requires full-time enrollment (12+ credits). "
                    "Application deadline varies by program — contact International Admissions."
                ),
                metadata={"topic": "visa"},
            )

        lines = ["Available programs:"]
        for p in matched[:3]:
            reqs = "; ".join(p["requirements"])
            lines.append(
                f"  • {p['name']} ({p['level']}) — {p['department']}\n"
                f"    Tuition: ${p['tuition_annual']:,}/year | Deadline: {p['deadline']}\n"
                f"    Requirements: {reqs}"
            )

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={"programs": matched[:3]},
        )
