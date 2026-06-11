from app.agents.base import Agent, AgentContext, AgentResult
from app.services.llm import llm_service
from app.services.rag import rag_service


class KnowledgeAgent(Agent):
    name = "knowledge"
    description = "University brain — policies, regulations, handbooks, and official documents"
    keywords = [
        "policy", "registration", "scholarship", "graduation", "requirement",
        "handbook", "transfer", "visa", "deadline", "form", "apply", "when is",
        "how do i", "what are the",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        results = await rag_service.search_hybrid(context.message, top_k=3)
        if not results:
            return AgentResult(
                agent=self.name,
                message=(
                    "I couldn't find a specific policy document matching your question. "
                    "Please contact the Registrar's Office or check the student handbook."
                ),
                metadata={"status": "no_results"},
            )

        citations = [r.to_citation() for r in results]
        chunks = [
            {
                "document_title": r.document_title,
                "excerpt": r.excerpt,
                "source_url": r.source_url,
            }
            for r in results
        ]
        answer = await llm_service.synthesize_answer(context.message, chunks)
        return AgentResult(
            agent=self.name,
            message=answer,
            citations=citations,
            metadata={"documents_matched": len(results), "search_mode": "hybrid"},
        )
