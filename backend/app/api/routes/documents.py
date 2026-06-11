from fastapi import APIRouter

from app.schemas import DocumentResponse
from app.services.rag import rag_service

router = APIRouter()


@router.get("/", response_model=list[DocumentResponse])
async def list_documents():
    docs = rag_service.list_documents()
    return [
        DocumentResponse(
            id=doc["id"],  # type: ignore[arg-type]
            title=doc["title"],
            category=doc["category"],
            source_url=doc.get("source_url"),
            created_at=doc["created_at"],
        )
        for doc in docs
    ]
