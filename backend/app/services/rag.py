from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.schemas import Citation


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


DEMO_DOCUMENTS = [
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
    },
]


class RAGService:
    """Retrieval-Augmented Generation service (Phase 0: keyword search stub)."""

    def list_documents(self) -> list[dict]:
        return DEMO_DOCUMENTS

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
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
        results = []
        for score, doc in scored[:top_k]:
            results.append(
                SearchResult(
                    document_id=doc["id"],
                    document_title=doc["title"],
                    excerpt=doc["content"][:300],
                    source_url=doc.get("source_url"),
                    score=score,
                )
            )
        return results

    async def ingest_document(
        self,
        title: str,
        content: str,
        category: str,
        source_url: str | None = None,
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
            }
        )
        return doc_id


rag_service = RAGService()
