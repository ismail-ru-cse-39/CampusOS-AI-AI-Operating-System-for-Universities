import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.usage_limits import (
    LLMUsageContext,
    UsageLimitExceeded,
    usage_limit_service,
)


@pytest.fixture(autouse=True)
def reset_usage_counters():
    usage_limit_service.reset_counters()
    usage_limit_service._redis_checked = True
    usage_limit_service._redis = None
    yield
    usage_limit_service.reset_counters()
    usage_limit_service._redis_checked = True
    usage_limit_service._redis = None


def test_free_tier_blocks_real_llm():
    context = LLMUsageContext(
        university_id="free-uni",
        user_id="user-1",
        user_role="student",
        plan="free",
    )
    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.llm_model = "gpt-4o-mini"
        result = asyncio.run(
            __import__("app.services.llm", fromlist=["llm_service"]).llm_service.complete(
                "What is the registration deadline?",
                usage=context,
            )
        )
    assert "[LLM stub]" in result
    snapshot = usage_limit_service.get_usage_snapshot("free-uni", "user-1", "free", "student")
    assert snapshot["university_calls_today"] == 0


def test_starter_tier_allows_calls_under_limit():
    context = LLMUsageContext(
        university_id="starter-uni",
        user_id="user-2",
        user_role="admin",
        plan="starter",
    )
    limits = usage_limit_service.check_can_make_llm_call(context)
    assert limits.daily_llm_calls_university == 500
    usage_limit_service.record_llm_usage(context, tokens_used=120)
    snapshot = usage_limit_service.get_usage_snapshot("starter-uni", "user-2", "starter", "admin")
    assert snapshot["university_calls_today"] == 1
    assert snapshot["user_calls_today"] == 1
    assert snapshot["tokens_today"] == 120


def test_429_when_over_daily_cap():
    context = LLMUsageContext(
        university_id="cap-uni",
        user_id="user-3",
        user_role="student",
        plan="starter",
    )
    for _ in range(50):
        usage_limit_service.record_llm_usage(context, tokens_used=10)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "What is the scholarship policy?",
                "user_role": "student",
                "user_id": "user-3",
                "university_slug": "cap-uni",
                "plan": "starter",
            },
        )
    assert response.status_code == 429
    assert "Daily LLM call limit" in response.json()["detail"]


def test_role_modifier_applied():
    starter_student = usage_limit_service.get_effective_limits("starter", "student")
    starter_admin = usage_limit_service.get_effective_limits("starter", "admin")
    assert starter_student.daily_llm_calls_user == 50
    assert starter_admin.daily_llm_calls_user == 500
    assert starter_student.daily_llm_calls_university == 500

    context = LLMUsageContext(
        university_id="role-uni",
        user_id="student-1",
        user_role="student",
        plan="starter",
    )
    for _ in range(50):
        usage_limit_service.record_llm_usage(context)

    with pytest.raises(UsageLimitExceeded) as exc_info:
        usage_limit_service.check_can_make_llm_call(context)
    assert exc_info.value.limit_type == "user_daily"


def test_starter_openai_call_records_usage_when_mocked():
    context = LLMUsageContext(
        university_id="mock-uni",
        user_id="user-4",
        user_role="admin",
        plan="starter",
    )
    mock_response = {
        "choices": [{"message": {"content": "Registration opens August 15."}}],
        "usage": {"total_tokens": 42},
    }
    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.llm_model = "gpt-4o-mini"
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_resp = AsyncMock()
            mock_resp.raise_for_status = lambda: None
            mock_resp.json = lambda: mock_response
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            from app.services.llm import llm_service

            result = asyncio.run(llm_service.complete("Hello", usage=context))

    assert result == "Registration opens August 15."
    snapshot = usage_limit_service.get_usage_snapshot("mock-uni", "user-4", "starter", "admin")
    assert snapshot["university_calls_today"] == 1
    assert snapshot["tokens_today"] == 42
