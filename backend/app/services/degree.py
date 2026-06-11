from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Demo program requirements (DB-backed via ProgramRequirement model when available)
DEMO_PROGRAM_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "BSc Computer Science": {
        "total_credits": 120,
        "min_gpa": 2.0,
        "core_courses": [
            "CS101", "CS201", "CS301", "CS350", "CS401", "MATH101", "MATH301",
        ],
        "elective_credits": 24,
        "capstone": "CS401",
    },
    "MSc Data Science": {
        "total_credits": 36,
        "min_gpa": 3.0,
        "core_courses": ["DS501", "DS502", "DS503", "STAT501"],
        "elective_credits": 9,
        "capstone": "DS599",
    },
}

CAREER_PATHWAYS: dict[str, dict[str, Any]] = {
    "ai engineer": {
        "title": "AI Engineer Pathway",
        "recommended_electives": ["CS401 Machine Learning", "CS420 Deep Learning", "CS450 NLP"],
        "skills": ["Python", "TensorFlow/PyTorch", "MLOps", "Statistics"],
        "semesters_remaining": 3,
    },
    "data scientist": {
        "title": "Data Scientist Pathway",
        "recommended_electives": ["CS401 Machine Learning", "MATH301 Statistics", "DS502 Data Mining"],
        "skills": ["Python", "SQL", "Statistics", "Visualization"],
        "semesters_remaining": 3,
    },
    "software engineer": {
        "title": "Software Engineer Pathway",
        "recommended_electives": ["CS350 Databases", "CS380 Software Engineering", "CS310 Systems"],
        "skills": ["Algorithms", "System Design", "Testing", "CI/CD"],
        "semesters_remaining": 2,
    },
}


@dataclass
class GraduationEligibility:
    eligible: bool
    credits_earned: int
    credits_required: int
    credits_remaining: int
    missing_core: list[str]
    gpa_met: bool
    academic_standing_ok: bool
    summary: str


class DegreeRequirementsEngine:
    def get_program_requirements(self, program: str) -> dict[str, Any]:
        return DEMO_PROGRAM_REQUIREMENTS.get(
            program,
            {
                "total_credits": 120,
                "min_gpa": 2.0,
                "core_courses": [],
                "elective_credits": 24,
                "capstone": None,
            },
        )

    def assess_graduation(
        self,
        *,
        program: str,
        credits_earned: int,
        completed_course_codes: list[str],
        academic_standing: str = "good",
        gpa: float = 3.0,
    ) -> GraduationEligibility:
        reqs = self.get_program_requirements(program)
        required = reqs["total_credits"]
        remaining = max(0, required - credits_earned)
        core = reqs.get("core_courses", [])
        missing_core = [c for c in core if c not in completed_course_codes]
        gpa_met = gpa >= reqs.get("min_gpa", 2.0)
        standing_ok = academic_standing in ("good", "probation") or academic_standing == "good"
        eligible = remaining == 0 and not missing_core and gpa_met and standing_ok

        if eligible:
            summary = "You meet all graduation requirements."
        elif remaining > 0:
            summary = f"You need {remaining} more credits to graduate."
        elif missing_core:
            summary = f"Missing core courses: {', '.join(missing_core)}."
        else:
            summary = "Review academic standing and GPA requirements."

        return GraduationEligibility(
            eligible=eligible,
            credits_earned=credits_earned,
            credits_required=required,
            credits_remaining=remaining,
            missing_core=missing_core,
            gpa_met=gpa_met,
            academic_standing_ok=standing_ok,
            summary=summary,
        )

    def build_roadmap(
        self,
        *,
        program: str,
        credits_earned: int,
        completed_course_codes: list[str],
        career_goal: str | None = None,
    ) -> dict[str, Any]:
        reqs = self.get_program_requirements(program)
        remaining_credits = max(0, reqs["total_credits"] - credits_earned)
        missing_core = [c for c in reqs.get("core_courses", []) if c not in completed_course_codes]

        pathway = None
        if career_goal:
            key = career_goal.lower()
            for name, data in CAREER_PATHWAYS.items():
                if name in key or key in name:
                    pathway = data
                    break

        semesters = []
        credits_per_semester = 15
        credits_left = remaining_credits
        semester_num = 1
        while credits_left > 0 and semester_num <= 4:
            load = min(credits_per_semester, credits_left)
            courses: list[str] = []
            if semester_num == 1 and missing_core:
                courses.extend(missing_core[:3])
            if pathway:
                courses.extend(pathway["recommended_electives"][:2])
            semesters.append(
                {
                    "semester": semester_num,
                    "credits": load,
                    "suggested_courses": courses or [f"Elective block ({load} credits)"],
                }
            )
            credits_left -= load
            semester_num += 1

        return {
            "program": program,
            "credits_remaining": remaining_credits,
            "missing_core": missing_core,
            "semesters": semesters,
            "career_pathway": pathway,
        }


degree_engine = DegreeRequirementsEngine()
