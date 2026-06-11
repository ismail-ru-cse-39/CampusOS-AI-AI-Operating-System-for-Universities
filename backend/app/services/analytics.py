from __future__ import annotations

from typing import Any

from app.services.retention import retention_service


class AnalyticsService:
    """Executive metrics from demo data and retention scoring."""

    def get_executive_metrics(self) -> dict[str, Any]:
        at_risk = retention_service.at_risk_students("medium")
        total_students = 12450
        at_risk_count = len(at_risk)

        return {
            "student_satisfaction": {"value": 4.2, "unit": "/ 5", "trend": "+0.3"},
            "retention_rate": {"value": 87.4, "unit": "%", "trend": "+1.2%"},
            "enrollment_forecast": {"value": total_students, "unit": "students", "trend": "+3.1%"},
            "at_risk_students": {"value": at_risk_count, "unit": "students", "trend": f"-{max(0, 8 - at_risk_count)}"},
            "support_tickets": {"value": 1203, "unit": "tickets", "trend": "-15%"},
            "avg_response_time": {"value": 2.4, "unit": "min", "trend": "-40%"},
            "department_performance": [
                {"department": "Engineering", "retention": 85.2, "enrollment": 3200},
                {"department": "Business", "retention": 89.1, "enrollment": 2800},
                {"department": "Arts", "retention": 91.5, "enrollment": 1900},
            ],
            "retention_trends": [
                {"semester": "2024-Fall", "rate": 85.1},
                {"semester": "2025-Spring", "rate": 86.3},
                {"semester": "2025-Fall", "rate": 87.4},
            ],
        }

    def generate_weekly_report(self) -> dict[str, Any]:
        metrics = self.get_executive_metrics()
        at_risk = retention_service.at_risk_students("high")
        return {
            "title": "Weekly Executive Intelligence Report",
            "period": "2026-W24",
            "summary": (
                f"Retention rate at {metrics['retention_rate']['value']}%. "
                f"{len(at_risk)} students at high/critical risk. "
                "Focus: Engineering retention, registration bottlenecks, career placement."
            ),
            "highlights": [
                "Enrollment forecast up 3.1% for Fall 2026",
                f"{len(at_risk)} students require immediate intervention",
                "Average AI response time reduced to 2.4 minutes",
            ],
            "recommendations": [
                "Expand tutoring in CS401 and MATH301",
                "Automate registration reminder workflows",
                "Launch career fair outreach for at-risk seniors",
            ],
            "metrics": metrics,
        }


analytics_service = AnalyticsService()
