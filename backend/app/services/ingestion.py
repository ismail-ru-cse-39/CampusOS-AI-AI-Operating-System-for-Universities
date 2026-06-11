from __future__ import annotations

import re
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm import llm_service


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


class IngestionService:
    """Document ingestion pipeline — chunk and embed (mock embeddings without API key)."""

    async def ingest_text(
        self,
        db: Optional[AsyncSession],
        *,
        title: str,
        content: str,
        category: str,
        university_id: Optional[UUID] = None,
        source_url: Optional[str] = None,
    ) -> UUID:
        from app.services.rag import rag_service

        doc_id = await rag_service.ingest_document(
            db=db,
            title=title,
            content=content,
            category=category,
            source_url=source_url,
            university_id=university_id,
        )
        chunks = chunk_text(content)
        for idx, chunk_content in enumerate(chunks):
            embedding = await llm_service.embed(chunk_content)
            await rag_service.store_chunk(
                db=db,
                document_id=doc_id,
                chunk_index=idx,
                content=chunk_content,
                embedding=embedding,
            )
        return doc_id

    async def ingest_upload(
        self,
        db: Optional[AsyncSession],
        *,
        filename: str,
        raw_bytes: bytes,
        category: str,
        university_id: Optional[UUID] = None,
    ) -> UUID:
        title = filename.rsplit(".", 1)[0] or filename
        content = self._extract_text(filename, raw_bytes)
        return await self.ingest_text(
            db,
            title=title,
            content=content,
            category=category,
            university_id=university_id,
        )

    def _extract_text(self, filename: str, raw_bytes: bytes) -> str:
        lower = filename.lower()
        if lower.endswith((".txt", ".md", ".html", ".htm")):
            return raw_bytes.decode("utf-8", errors="replace")
        # PDF/DOCX parsing deferred — store placeholder for pipeline structure
        return (
            f"[Binary upload: {filename}, {len(raw_bytes)} bytes. "
            "Full PDF/DOCX parsing requires document parser dependencies.]"
        )


ingestion_service = IngestionService()
