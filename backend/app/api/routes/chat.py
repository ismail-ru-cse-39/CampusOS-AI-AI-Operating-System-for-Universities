from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.orchestrator import Orchestrator
from app.core.config import settings
from app.core.deps import CurrentUser, DbSession, get_current_user_optional
from app.core.rbac import has_permission, parse_role
from app.schemas import ChatRequest, ChatResponse
from app.services.audit import log_audit
from app.services.usage_limits import LLMUsageContext, UsageLimitExceeded, usage_limit_service

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: DbSession,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
) -> ChatResponse:
    role = current_user.role.value if current_user else request.user_role
    if not has_permission(parse_role(role), "chat"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat not permitted for this role")

    user_id = request.user_id
    if current_user and current_user.id:
        user_id = str(current_user.id)

    university_id = request.university_slug or settings.default_university_slug
    plan = usage_limit_service.resolve_plan(
        plan=request.plan,
        university_slug=university_id,
    )

    usage_context = LLMUsageContext(
        university_id=university_id,
        user_id=user_id,
        user_role=role,
        plan=plan,
    )
    limits = usage_limit_service.get_effective_limits(plan, role)
    if limits.daily_llm_calls_university > 0:
        try:
            usage_limit_service.check_can_make_llm_call(usage_context)
        except UsageLimitExceeded as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(exc),
            ) from exc

    try:
        result = await orchestrator.route(
            message=request.message,
            user_role=role,
            user_id=user_id,
            db=db,
            language=request.language,
            university_id=university_id,
            plan=plan,
        )
    except UsageLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    audit_user_id: UUID | None = None
    if current_user and current_user.id:
        audit_user_id = current_user.id
    elif user_id:
        try:
            audit_user_id = UUID(user_id)
        except ValueError:
            audit_user_id = None

    await log_audit(
        db,
        user_id=audit_user_id,
        action="chat.request",
        resource="chat",
        details={
            "agent": result.agent,
            "user_role": role,
            "university_id": university_id,
            "plan": plan,
            "message_preview": request.message[:200],
        },
    )

    return ChatResponse(
        agent=result.agent,
        message=result.message,
        citations=result.citations,
        metadata=result.metadata,
    )
