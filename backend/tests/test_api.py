from fastapi.testclient import TestClient

from app.main import app


def test_health_lists_twelve_agents():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["agents_registered"] == 12


def test_chat_routes_student_success():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"message": "How many credits do I have left?", "user_role": "student"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == "student_success"


def test_auth_dev_token_and_me():
    with TestClient(app) as client:
        token_resp = client.post(
            "/api/v1/auth/dev-token",
            json={"email": "demo@campusos.edu", "role": "student"},
        )
        assert token_resp.status_code == 200
        token = token_resp.json()["access_token"]
        me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "student"


def test_chat_admin_assistant_workflow():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"message": "Request my official transcript", "user_role": "student"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == "admin_assistant"
    assert "workflow_id" in body["metadata"]


def test_student_progress_requires_auth():
    with TestClient(app) as client:
        response = client.get("/api/v1/students/progress")
    assert response.status_code == 401


def test_executive_analytics_requires_auth():
    with TestClient(app) as client:
        response = client.get("/api/v1/analytics/executive")
    assert response.status_code == 401


def test_weekly_report_with_executive_token():
    with TestClient(app) as client:
        token = client.post(
            "/api/v1/auth/dev-token",
            json={"email": "exec@campusos.edu", "role": "executive"},
        ).json()["access_token"]
        response = client.get(
            "/api/v1/analytics/weekly-report",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert "summary" in response.json()


def test_graph_query():
    with TestClient(app) as client:
        token = client.post(
            "/api/v1/auth/dev-token",
            json={"email": "demo@campusos.edu", "role": "student"},
        ).json()["access_token"]
        response = client.get(
            "/api/v1/graph/query?pattern=program:bsc-cs%20requires_course",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert len(response.json()["results"]) >= 1


def test_i18n_languages():
    with TestClient(app) as client:
        response = client.get("/api/v1/i18n/languages")
    assert response.status_code == 200
    langs = response.json()["languages"]
    assert "en" in langs
    assert "ar" in langs


def test_tenant_config():
    with TestClient(app) as client:
        response = client.get("/api/v1/tenants/demo-university")
    assert response.status_code == 200
    assert response.json()["slug"] == "demo-university"
