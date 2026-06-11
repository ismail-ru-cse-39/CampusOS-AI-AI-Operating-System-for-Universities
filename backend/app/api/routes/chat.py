from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends

from app.agents.orchestrator import Orchestrator
from app.core.deps import CurrentUser, DbSession, get_current_user_optional
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
    result = await orchestrator.route(
        message=request.message,
        user_role=request.user_role,
        user_id=request.user_id,
    )
    user_id = current_user.id if current_user and current_user.id else None
    if user_id is None and request.user_id:
        try:
            from uuid import UUID

            user_id = UUID(request.user_id)
        except ValueError:
            user_id = None

    await log_audit(
        db,
        user_id=user_id,
        action="chat.request",
        resource="chat",
        details={
            "agent": result.agent,
            "user_role": request.user_role,
            "message_preview": request.message[:200],
        },
    )

    return ChatResponse(
        agent=result.agent,
        message=result.message,
        citations=result.citations,
        metadata=result.metadata,
    )
