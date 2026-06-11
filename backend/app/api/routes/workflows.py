from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas import WorkflowResponse
from app.services.workflow_engine import workflow_engine

router = APIRouter()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: UUID) -> WorkflowResponse:
    result = await workflow_engine.get_status(workflow_id)
    if result.get("status") == "failed" and result.get("message") == "Workflow not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowResponse(
        workflow_id=result.get("workflow_id"),
        workflow_type=result.get("workflow_type", "unknown"),
        status=result.get("status", "unknown"),
        message=result.get("message", ""),
        tracking_url=result.get("tracking_url"),
        metadata=result,
    )
