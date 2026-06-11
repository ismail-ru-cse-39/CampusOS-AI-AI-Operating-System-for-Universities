from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Citation
from app.services.llm import llm_service


@dataclass
class SearchResult:
    document_id: UUID
    document_title: str
    excerpt: str
    source_url: str | None
    score: float

    def to_citation(self) -> Citation:
        return Citation(
            document_title=self.document_title,
            source_url=self.source_url,
            excerpt=self.excerpt,
        )


DEMO_DOCUMENTS: list[dict] = [
    {
        "id": UUID("10000000-0000-4000-8000-000000000001"),
        "title": "Student Registration Policy 2026",
        "category": "policy",
        "source_url": "https://demo-university.edu/policies/registration",
        "content": (
            "Registration for the Fall 2026 semester opens on August 15, 2026. "
            "Students must complete registration by September 1, 2026. "
            "Late registration incurs a $50 fee."
        ),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "chunks": [],
    },
    {
        "id": UUID("10000000-0000-4000-8000-000000000002"),
        "title": "Graduation Requirements Handbook",
        "category": "handbook",
        "source_url": "https://demo-university.edu/handbooks/graduation",
        "content": (
            "To graduate, students must complete 120 credits with a minimum GPA of 2.0. "
            "All core program requirements must be satisfied. "
            "Students must apply for graduation at least one semester in advance."
        ),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "chunks": [],
    },
    {
        "id": UUID("10000000-0000-4000-8000-000000000003"),
        "title": "Scholarship Application Guide",
        "category": "guide",
        "source_url": "https://demo-university.edu/financial-aid/scholarships",
        "content": (
            "Scholarship applications open March 1 each year. "
            "Required documents: transcript, personal statement, and two reference letters. "
            "Minimum GPA requirement: 3.0 for merit scholarships."
        ),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "chunks": [],
    },
    {
        "id": UUID("10000000-0000-4000-8000-000000000004"),
        "title": "Department Transfer Policy",
        "category": "policy",
        "source_url": "https://demo-university.edu/policies/transfer",
        "content": (
            "Students may transfer departments after completing their first year. "
            "Submit a transfer request form to the Registrar. "
            "Minimum GPA of 2.5 required for internal transfers."
        ),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "chunks": [],
    },
    {
        "id": UUID("10000000-0000-4000-8000-000000000005"),
        "title": "International Student Visa Guide",
        "category": "guide",
        "source_url": "https://demo-university.edu/international/visa",
        "content": (
            "International students must maintain valid visa status throughout enrollment. "
            "Contact the International Office for visa renewal at least 60 days before expiry. "
            "Full-time enrollment (12+ credits) is required for F-1 visa holders."
        ),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "chunks": [],
    },
]

# In-memory chunk store for dev (DB when available)
_CHUNK_STORE: list[dict] = []


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (norm_a * norm_b)


class RAGService:
    """Retrieval-Augmented Generation — keyword + pgvector semantic search."""

    def list_documents(self) -> list[dict]:
        return DEMO_DOCUMENTS

    def _keyword_search(self, query: str, top_k: int) -> list[SearchResult]:
        query_lower = query.lower()
        scored: list[tuple[float, dict]] = []
        for doc in DEMO_DOCUMENTS:
            content_lower = doc["content"].lower()
            title_lower = doc["title"].lower()
            score = 0.0
            for word in query_lower.split():
                word = word.strip(".,!?;:'\"")
                if len(word) < 3:
                    continue
                if word in content_lower:
                    score += 1.0
                if word in title_lower:
                    score += 2.0
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            SearchResult(
                document_id=doc["id"],
                document_title=doc["title"],
                excerpt=doc["content"][:300],
                source_url=doc.get("source_url"),
                score=score,
            )
            for score, doc in scored[:top_k]
        ]

    async def semantic_search(
        self,
        query: str,
        top_k: int = 3,
        db: Optional[AsyncSession] = None,
    ) -> list[SearchResult]:
        query_embedding = await llm_service.embed(query)

        # Try DB pgvector search
        if db is not None:
            try:
                from app.models import Document, DocumentChunk

                result = await db.execute(
                    select(DocumentChunk, Document)
                    .join(Document, DocumentChunk.document_id == Document.id)
                )
                rows = result.all()
                if rows:
                    scored: list[tuple[float, DocumentChunk, Document]] = []
                    for chunk, doc in rows:
                        emb = chunk.embedding
                        if emb is None:
                            continue
                        if isinstance(emb, str):
                            continue
                        sim = _cosine_similarity(query_embedding, list(emb))
                        scored.append((sim, chunk, doc))
                    scored.sort(key=lambda x: x[0], reverse=True)
                    return [
                        SearchResult(
                            document_id=doc.id,
                            document_title=doc.title,
                            excerpt=chunk.content[:300],
                            source_url=doc.source_url,
                            score=sim,
                        )
                        for sim, chunk, doc in scored[:top_k]
                        if sim > 0
                    ]
            except Exception:
                pass

        # In-memory chunk store fallback
        scored_mem: list[tuple[float, dict]] = []
        for chunk in _CHUNK_STORE:
            emb = chunk.get("embedding")
            if not emb:
                continue
            sim = _cosine_similarity(query_embedding, emb)
            scored_mem.append((sim, chunk))
        scored_mem.sort(key=lambda x: x[0], reverse=True)

        if scored_mem:
            results = []
            for sim, chunk in scored_mem[:top_k]:
                doc = next((d for d in DEMO_DOCUMENTS if d["id"] == chunk["document_id"]), None)
                if doc:
                    results.append(
                        SearchResult(
                            document_id=doc["id"],
                            document_title=doc["title"],
                            excerpt=chunk["content"][:300],
                            source_url=doc.get("source_url"),
                            score=sim,
                        )
                    )
            if results:
                return results

        # Bootstrap embeddings from demo docs on first semantic query
        for doc in DEMO_DOCUMENTS:
            emb = await llm_service.embed(doc["content"])
            _CHUNK_STORE.append(
                {
                    "document_id": doc["id"],
                    "content": doc["content"],
                    "embedding": emb,
                }
            )
        return await self.semantic_search(query, top_k=top_k, db=db)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        return self._keyword_search(query, top_k)

    async def search_hybrid(
        self,
        query: str,
        top_k: int = 3,
        db: Optional[AsyncSession] = None,
    ) -> list[SearchResult]:
        keyword = self._keyword_search(query, top_k)
        semantic = await self.semantic_search(query, top_k, db=db)
        seen: set[UUID] = set()
        merged: list[SearchResult] = []
        for r in semantic + keyword:
            if r.document_id not in seen:
                seen.add(r.document_id)
                merged.append(r)
        merged.sort(key=lambda x: x.score, reverse=True)
        return merged[:top_k]

    async def ingest_document(
        self,
        title: str,
        content: str,
        category: str,
        source_url: str | None = None,
        db: Optional[AsyncSession] = None,
        university_id: Optional[UUID] = None,
    ) -> UUID:
        doc_id = uuid4()
        DEMO_DOCUMENTS.append(
            {
                "id": doc_id,
                "title": title,
                "category": category,
                "source_url": source_url,
                "content": content,
                "created_at": datetime.now(timezone.utc),
                "chunks": [],
            }
        )
        if db is not None and university_id is not None:
            try:
                from app.models import Document

                doc = Document(
                    id=doc_id,
                    university_id=university_id,
                    title=title,
                    category=category,
                    source_url=source_url,
                    content=content,
                )
                db.add(doc)
                await db.commit()
            except Exception:
                await db.rollback()
        return doc_id

    async def store_chunk(
        self,
        document_id: UUID,
        chunk_index: int,
        content: str,
        embedding: list[float],
        db: Optional[AsyncSession] = None,
    ) -> None:
        _CHUNK_STORE.append(
            {
                "document_id": document_id,
                "chunk_index": chunk_index,
                "content": content,
                "embedding": embedding,
            }
        )
        if db is not None:
            try:
                from app.models import DocumentChunk

                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    content=content,
                    embedding=embedding,
                )
                db.add(chunk)
                await db.commit()
            except Exception:
                await db.rollback()


rag_service = RAGService()
