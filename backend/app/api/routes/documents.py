from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.deps import CurrentUser, DbSession, require_permission
from app.schemas import DocumentResponse, DocumentUploadResponse
from app.services.audit import log_audit
from app.services.ingestion import chunk_text, ingestion_service
from app.services.rag import rag_service

router = APIRouter()


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    current_user: Annotated[CurrentUser, Depends(require_permission("view_public_documents"))],
):
    docs = rag_service.list_documents()
    return [
        DocumentResponse(
            id=doc["id"],
            title=doc["title"],
            category=doc["category"],
            source_url=doc.get("source_url"),
            created_at=doc["created_at"],
        )
        for doc in docs
    ]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    db: DbSession,
    current_user: Annotated[CurrentUser, Depends(require_permission("manage_documents"))],
    file: UploadFile = File(...),
    category: str = Form("policy"),
    university_id: Optional[str] = Form(None),
):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    uid: UUID | None = None
    if university_id:
        try:
            uid = UUID(university_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid university_id")

    doc_id = await ingestion_service.ingest_upload(
        db,
        filename=file.filename or "upload.txt",
        raw_bytes=raw,
        category=category,
        university_id=uid,
    )

    content = ingestion_service._extract_text(file.filename or "upload.txt", raw)
    chunks = chunk_text(content)

    await log_audit(
        db,
        user_id=current_user.id,
        action="document.upload",
        resource="documents",
        details={"document_id": str(doc_id), "filename": file.filename, "category": category},
    )

    return DocumentUploadResponse(
        document_id=doc_id,
        title=(file.filename or "upload").rsplit(".", 1)[0],
        chunks_created=len(chunks),
        message="Document ingested (mock embeddings without OPENAI_API_KEY)",
    )
