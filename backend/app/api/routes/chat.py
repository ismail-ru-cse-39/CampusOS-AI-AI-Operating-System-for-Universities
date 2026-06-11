from fastapi import APIRouter

from app.agents.orchestrator import Orchestrator
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await orchestrator.route(
        message=request.message,
        user_role=request.user_role,
        user_id=request.user_id,
    )
    return ChatResponse(
        agent=result.agent,
        message=result.message,
        citations=result.citations,
        metadata=result.metadata,
    )
