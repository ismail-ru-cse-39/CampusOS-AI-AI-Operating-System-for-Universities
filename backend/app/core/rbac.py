from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
    ADMISSIONS = "admissions"
    CAREER_SERVICES = "career_services"
    EXECUTIVE = "executive"


ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.STUDENT: {
        "chat",
        "view_own_profile",
        "view_own_courses",
        "view_public_documents",
        "execute_workflows",
    },
    UserRole.FACULTY: {
        "chat",
        "view_own_profile",
        "view_student_roster",
        "view_course_analytics",
        "view_public_documents",
        "view_predictive_analytics",
    },
    UserRole.ADMIN: {
        "chat",
        "view_all_students",
        "manage_documents",
        "execute_workflows",
        "view_audit_logs",
        "view_dashboards",
        "view_predictive_analytics",
    },
    UserRole.ADMISSIONS: {
        "chat",
        "view_prospect_data",
        "manage_applications",
    },
    UserRole.CAREER_SERVICES: {
        "chat",
        "view_student_profiles",
        "manage_opportunities",
    },
    UserRole.EXECUTIVE: {
        "chat",
        "view_dashboards",
        "view_predictive_analytics",
        "view_audit_logs",
    },
}

# Minimum permission required to invoke each agent
AGENT_PERMISSIONS: dict[str, str] = {
    "knowledge": "chat",
    "student_success": "view_own_profile",
    "academic_advisor": "view_own_profile",
    "timetable": "view_own_courses",
    "campus_navigation": "chat",
    "career": "view_own_profile",
    "admissions": "view_prospect_data",
    "admin_assistant": "execute_workflows",
    "faculty_intelligence": "view_course_analytics",
    "retention": "view_predictive_analytics",
    "research_assistant": "chat",
    "executive_intelligence": "view_dashboards",
}

# Roles allowed to invoke each agent (additional guard beyond permission)
AGENT_ROLE_ALLOWLIST: dict[str, set[UserRole] | None] = {
    "knowledge": None,
    "student_success": {UserRole.STUDENT, UserRole.ADMIN},
    "academic_advisor": {UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN},
    "timetable": {UserRole.STUDENT, UserRole.ADMIN},
    "campus_navigation": None,
    "career": {UserRole.STUDENT, UserRole.CAREER_SERVICES, UserRole.ADMIN},
    "admissions": None,
    "admin_assistant": {UserRole.STUDENT, UserRole.ADMIN},
    "faculty_intelligence": {UserRole.FACULTY, UserRole.EXECUTIVE, UserRole.ADMIN},
    "retention": {UserRole.FACULTY, UserRole.EXECUTIVE, UserRole.ADMIN},
    "research_assistant": {UserRole.FACULTY, UserRole.ADMIN},
    "executive_intelligence": {UserRole.EXECUTIVE, UserRole.ADMIN},
}


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def can_access_agent(role: UserRole, agent_name: str) -> bool:
    permission = AGENT_PERMISSIONS.get(agent_name, "chat")
    if not has_permission(role, permission):
        return False
    allowlist = AGENT_ROLE_ALLOWLIST.get(agent_name)
    if allowlist is None:
        return True
    return role in allowlist


def parse_role(role: str) -> UserRole:
    try:
        return UserRole(role.lower())
    except ValueError:
        return UserRole.STUDENT
