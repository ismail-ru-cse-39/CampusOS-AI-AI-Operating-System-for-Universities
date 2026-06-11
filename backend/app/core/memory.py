from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StudentMemory:
    """Personalized student context for agent conversations."""

    user_id: str
    full_name: str = ""
    program: str = ""
    credits_earned: int = 0
    credits_required: int = 120
    current_courses: list[str] = field(default_factory=list)
    completed_courses: list[str] = field(default_factory=list)
    academic_standing: str = "good"
    career_interests: list[str] = field(default_factory=list)
    upcoming_deadlines: list[dict[str, Any]] = field(default_factory=list)

    def to_context(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "program": self.program,
            "credits_earned": self.credits_earned,
            "credits_required": self.credits_required,
            "credits_remaining": max(0, self.credits_required - self.credits_earned),
            "current_courses": self.current_courses,
            "completed_courses": self.completed_courses,
            "academic_standing": self.academic_standing,
            "career_interests": self.career_interests,
            "upcoming_deadlines": self.upcoming_deadlines,
        }


# Demo memory for Phase 0 (replaced by DB lookup in Phase 1)
DEMO_STUDENT_MEMORY = StudentMemory(
    user_id="00000000-0000-4000-8000-000000000001",
    full_name="Alex Johnson",
    program="BSc Computer Science",
    credits_earned=84,
    credits_required=120,
    current_courses=["CS401 Machine Learning", "CS350 Databases", "MATH301 Statistics"],
    completed_courses=["CS101 Intro to Programming", "CS201 Data Structures", "CS301 Algorithms"],
    academic_standing="good",
    career_interests=["AI Engineer", "Machine Learning"],
    upcoming_deadlines=[
        {"title": "Registration opens", "date": "2026-08-15"},
        {"title": "CS401 Final Project", "date": "2026-05-20"},
    ],
)
