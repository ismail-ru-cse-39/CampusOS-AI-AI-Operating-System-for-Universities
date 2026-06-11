from app.agents.base import Agent, AgentContext, AgentResult
from app.services.demo_data import CAREER_OPPORTUNITIES


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
        program = context.memory.get("program", "")
        lower = context.message.lower()

        opps = CAREER_OPPORTUNITIES
        if "internship" in lower:
            opps = [o for o in opps if o["type"] == "internship"]
        elif "job" in lower:
            opps = [o for o in opps if o["type"] in ("full_time", "part_time")]

        if interests:
            opps = [
                o for o in opps
                if any(i.lower() in " ".join(o["skills"]).lower() for i in interests)
            ] or CAREER_OPPORTUNITIES

        lines = [f"Career opportunities matching {program}:"]
        for o in opps[:3]:
            lines.append(
                f"  • {o['title']} at {o['company']} ({o['type']})\n"
                f"    Skills: {', '.join(o['skills'])} | Min GPA: {o['gpa_min']}"
            )

        if "resume" in lower or "cv" in lower:
            lines.append(
                "\nResume tips: highlight relevant projects, quantify achievements, "
                "tailor skills to each role, and include your GPA if above 3.0."
            )

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={"opportunities": opps[:3], "career_interests": interests},
        )
