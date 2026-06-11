from app.agents.base import Agent, AgentContext, AgentResult
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
        results = rag_service.search(context.message, top_k=3)
        if not results:
            return AgentResult(
                agent=self.name,
                message=(
                    "I couldn't find a specific policy document matching your question. "
                    "Please contact the Registrar's Office or check the student handbook."
                ),
                metadata={"status": "no_results"},
            )

        top = results[0]
        citations = [r.to_citation() for r in results]
        answer = (
            f"Based on official university documents:\n\n{top.excerpt}\n\n"
            f"Source: {top.document_title}"
        )
        return AgentResult(
            agent=self.name,
            message=answer,
            citations=citations,
            metadata={"documents_matched": len(results)},
        )
