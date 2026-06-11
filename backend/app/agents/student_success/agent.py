from app.agents.base import Agent, AgentContext, AgentResult
from app.services.degree import degree_engine


class StudentSuccessAgent(Agent):
    name = "student_success"
    description = "Academic guidance, graduation tracking, credit calculation, degree progress"
    keywords = [
        "credit", "graduate", "graduation", "degree", "progress", "gpa",
        "semester", "fail", "module", "course", "remaining", "standing",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        if user_role not in ("student", "admin"):
            return 0.0
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        memory = context.memory
        earned = memory.get("credits_earned", 0)
        required = memory.get("credits_required", 120)
        remaining = max(0, required - earned)
        program = memory.get("program", "your program")
        name = memory.get("full_name", "Student")
        completed_codes = [
            c.split()[0] for c in memory.get("completed_courses", []) if c
        ]

        lower = context.message.lower()
        if "graduate" in lower or "graduation" in lower:
            assessment = degree_engine.assess_graduation(
                program=program,
                credits_earned=earned,
                completed_course_codes=completed_codes,
                academic_standing=memory.get("academic_standing", "good"),
            )
            msg = (
                f"Hi {name}, you have {earned}/{assessment.credits_required} credits in {program}. "
                f"{assessment.summary}"
            )
            if assessment.missing_core:
                msg += f" Missing core: {', '.join(assessment.missing_core)}."
        elif "credit" in lower or "remaining" in lower:
            msg = (
                f"You have earned {earned} credits toward your {required}-credit degree in {program}. "
                f"You have {remaining} credits remaining."
            )
        elif "fail" in lower:
            msg = (
                "If you fail a module, you typically need to retake it or an approved equivalent. "
                "Check the academic standing policy — repeated failures may affect your enrollment status. "
                "I recommend meeting with your academic advisor to plan your next steps."
            )
        else:
            current = memory.get("current_courses", [])
            msg = (
                f"Based on your profile ({earned}/{required} credits in {program}), "
                f"you are currently enrolled in: {', '.join(current) or 'no active courses'}. "
                f"Your academic standing is: {memory.get('academic_standing', 'good')}."
            )

        return AgentResult(
            agent=self.name,
            message=msg,
            metadata={"credits_earned": earned, "credits_remaining": remaining},
        )
