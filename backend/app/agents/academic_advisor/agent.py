from app.agents.base import Agent, AgentContext, AgentResult
from app.services.degree import degree_engine


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
        memory = context.memory
        program = memory.get("program", "BSc Computer Science")
        earned = memory.get("credits_earned", 0)
        completed_codes = [
            c.split()[0] for c in memory.get("completed_courses", []) if c
        ]

        career_goal = None
        lower = context.message.lower()
        for goal in ("ai engineer", "data scientist", "software engineer"):
            if goal in lower:
                career_goal = goal
                break
        if "become" in lower and not career_goal:
            career_goal = context.message.split("become", 1)[-1].strip().rstrip("?")

        roadmap = degree_engine.build_roadmap(
            program=program,
            credits_earned=earned,
            completed_course_codes=completed_codes,
            career_goal=career_goal,
        )

        lines = [f"Degree roadmap for {program} ({roadmap['credits_remaining']} credits remaining):"]
        for sem in roadmap["semesters"]:
            courses = ", ".join(sem["suggested_courses"])
            lines.append(f"  Semester {sem['semester']}: {courses} ({sem['credits']} credits)")

        pathway = roadmap.get("career_pathway")
        if pathway:
            lines.append(f"\nCareer pathway: {pathway['title']}")
            lines.append(f"Recommended skills: {', '.join(pathway['skills'])}")

        if roadmap["missing_core"]:
            lines.append(f"\nPriority core courses: {', '.join(roadmap['missing_core'])}")

        return AgentResult(
            agent=self.name,
            message="\n".join(lines),
            metadata={"roadmap": roadmap},
        )
