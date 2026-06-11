from app.core.rbac import UserRole, can_access_agent, has_permission


def test_student_can_access_student_success():
    assert can_access_agent(UserRole.STUDENT, "student_success") is True


def test_student_cannot_access_retention():
    assert can_access_agent(UserRole.STUDENT, "retention") is False


def test_faculty_can_access_retention():
    assert can_access_agent(UserRole.FACULTY, "retention") is True


def test_executive_can_access_dashboard_agent():
    assert can_access_agent(UserRole.EXECUTIVE, "executive_intelligence") is True


def test_admin_can_manage_documents():
    assert has_permission(UserRole.ADMIN, "manage_documents") is True


def test_student_cannot_manage_documents():
    assert has_permission(UserRole.STUDENT, "manage_documents") is False
