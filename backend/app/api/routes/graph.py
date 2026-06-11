from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import require_permission
from app.schemas import GraphQueryResponse
from app.services.graph_sync import graph_sync_service
from app.services.knowledge_graph import knowledge_graph_service

router = APIRouter()


@router.get("/query", response_model=GraphQueryResponse)
async def graph_query(
    _: Annotated[object, Depends(require_permission("chat"))],
    pattern: str = Query(..., description="e.g. program:bsc-cs requires_course"),
):
    results = await knowledge_graph_service.query(pattern)
    return GraphQueryResponse(results=results, pattern=pattern)


@router.post("/sync")
async def sync_graph(
    _: Annotated[object, Depends(require_permission("view_audit_logs"))],
):
    return await graph_sync_service.sync_from_postgres()
