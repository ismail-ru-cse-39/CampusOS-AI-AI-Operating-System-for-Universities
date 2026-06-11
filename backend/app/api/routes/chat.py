from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from app.agents.orchestrator import Orchestrator
from app.core.deps import CurrentUser, DbSession, get_current_user_optional
from app.core.rbac import has_permission, parse_role
from app.schemas import ChatRequest, ChatResponse
from app.services.audit import log_audit

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
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat not permitted for this role")

    user_id = request.user_id
    if current_user and current_user.id:
        user_id = str(current_user.id)

    result = await orchestrator.route(
        message=request.message,
        user_role=role,
        user_id=user_id,
        db=db,
        language=request.language,
    )

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
            "message_preview": request.message[:200],
        },
    )

    return ChatResponse(
        agent=result.agent,
        message=result.message,
        citations=result.citations,
        metadata=result.metadata,
    )
