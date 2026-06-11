from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskScore:
    student_id: str
    student_name: str
    score: float
    risk_level: str
    signals: list[str]
    recommended_interventions: list[str]


DEMO_STUDENT_RISK_DATA: list[dict[str, Any]] = [
    {
        "student_id": "s001",
        "student_name": "Jordan Lee",
        "attendance_rate": 0.62,
        "gpa": 1.8,
        "assignments_missed": 4,
        "engagement_score": 0.4,
        "financial_hold": True,
    },
    {
        "student_id": "s002",
        "student_name": "Sam Patel",
        "attendance_rate": 0.88,
        "gpa": 3.1,
        "assignments_missed": 1,
        "engagement_score": 0.75,
        "financial_hold": False,
    },
    {
        "student_id": "s003",
        "student_name": "Taylor Kim",
        "attendance_rate": 0.55,
        "gpa": 2.0,
        "assignments_missed": 5,
        "engagement_score": 0.35,
        "financial_hold": False,
    },
    {
        "student_id": "s004",
        "student_name": "Alex Johnson",
        "attendance_rate": 0.92,
        "gpa": 3.4,
        "assignments_missed": 0,
        "engagement_score": 0.85,
        "financial_hold": False,
    },
]

INTERVENTION_PLAYBOOK: dict[str, list[str]] = {
    "critical": [
        "Schedule advisor meeting within 48 hours",
        "Connect with financial aid office",
        "Assign peer mentor",
    ],
    "high": [
        "Send attendance reminder",
        "Offer tutoring resources",
        "Faculty outreach email",
    ],
    "medium": [
        "Monitor for 2 weeks",
        "Suggest study skills workshop",
    ],
    "low": [
        "Continue standard support",
    ],
}


class RetentionScoringService:
    """Rule-based retention risk scoring (ML model in production)."""

    def score_student(self, data: dict[str, Any]) -> RiskScore:
        signals: list[str] = []
        score = 0.0

        attendance = data.get("attendance_rate", 1.0)
        if attendance < 0.7:
            score += 0.3
            signals.append(f"Low attendance ({attendance:.0%})")
        elif attendance < 0.85:
            score += 0.15
            signals.append(f"Declining attendance ({attendance:.0%})")

        gpa = data.get("gpa", 3.0)
        if gpa < 2.0:
            score += 0.35
            signals.append(f"GPA below 2.0 ({gpa})")
        elif gpa < 2.5:
            score += 0.2
            signals.append(f"GPA at risk ({gpa})")

        missed = data.get("assignments_missed", 0)
        if missed >= 3:
            score += 0.2
            signals.append(f"{missed} assignments missed")
        elif missed >= 1:
            score += 0.1
            signals.append(f"{missed} assignment(s) missed")

        engagement = data.get("engagement_score", 1.0)
        if engagement < 0.5:
            score += 0.15
            signals.append(f"Low engagement ({engagement:.0%})")

        if data.get("financial_hold"):
            score += 0.25
            signals.append("Financial hold on account")

        score = min(1.0, score)
        if score >= 0.7:
            level = "critical"
        elif score >= 0.5:
            level = "high"
        elif score >= 0.3:
            level = "medium"
        else:
            level = "low"

        return RiskScore(
            student_id=data.get("student_id", "unknown"),
            student_name=data.get("student_name", "Unknown"),
            score=round(score, 2),
            risk_level=level,
            signals=signals,
            recommended_interventions=INTERVENTION_PLAYBOOK[level],
        )

    def score_all(self) -> list[RiskScore]:
        return [self.score_student(d) for d in DEMO_STUDENT_RISK_DATA]

    def at_risk_students(self, min_level: str = "medium") -> list[RiskScore]:
        levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        threshold = levels.get(min_level, 1)
        return [
            s for s in self.score_all()
            if levels.get(s.risk_level, 0) >= threshold
        ]


retention_service = RetentionScoringService()
