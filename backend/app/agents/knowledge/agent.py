from app.agents.base import Agent, AgentContext, AgentResult
from app.services.llm import llm_service
from app.services.rag import rag_service
from app.services.usage_limits import LLMUsageContext, usage_limit_service


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

        limits = usage_limit_service.get_effective_limits(context.plan, context.user_role)
        usage = LLMUsageContext(
            university_id=context.university_id,
            user_id=context.user_id,
            user_role=context.user_role,
            plan=context.plan,
        )

        if limits.llm_synthesis_enabled:
            answer = await llm_service.synthesize_answer(context.message, chunks, usage=usage)
            search_mode = "hybrid+synthesis"
        else:
            top = chunks[0]
            answer = (
                f"Based on official university documents:\n\n{top.get('excerpt', '')}\n\n"
                f"Source: {top.get('document_title', 'Unknown')}"
            )
            search_mode = "hybrid+excerpt"

        return AgentResult(
            agent=self.name,
            message=answer,
            citations=citations,
            metadata={
                "documents_matched": len(results),
                "search_mode": search_mode,
                "plan": context.plan,
            },
        )
