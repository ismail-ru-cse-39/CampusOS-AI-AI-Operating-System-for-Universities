from fastapi import APIRouter

from app.agents.registry import agent_registry
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=dict)
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "agents_registered": len(agent_registry.all()),
    }
