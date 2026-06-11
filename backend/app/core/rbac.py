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
    },
    UserRole.FACULTY: {
        "chat",
        "view_own_profile",
        "view_student_roster",
        "view_course_analytics",
        "view_public_documents",
    },
    UserRole.ADMIN: {
        "chat",
        "view_all_students",
        "manage_documents",
        "execute_workflows",
        "view_audit_logs",
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


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
