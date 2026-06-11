from uuid import UUID

from app.agents.base import Agent, AgentContext, AgentResult
from app.services.workflow_engine import WorkflowType, workflow_engine


class AdminAssistantAgent(Agent):
    name = "admin_assistant"
    description = "Automate university services — transcripts, enrollment verification, appointments"
    keywords = [
        "transcript", "verification", "appointment", "book", "submit", "form",
        "request", "status", "document request",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        score = self._keyword_score(message)
        if user_role in ("admin", "student"):
            return score
        return score * 0.5

    async def run(self, context: AgentContext) -> AgentResult:
        lower = context.message.lower()
        user_id = context.user_id or context.memory.get("user_id", "00000000-0000-4000-8000-000000000001")
        try:
            uid = UUID(str(user_id))
        except ValueError:
            uid = UUID("00000000-0000-4000-8000-000000000001")

        workflow_type = WorkflowType.TRANSCRIPT_REQUEST.value
        params: dict = {"student_verified": True}

        if "verification" in lower or "verify" in lower:
            workflow_type = WorkflowType.ENROLLMENT_VERIFICATION.value
        elif "appointment" in lower or "book" in lower:
            workflow_type = WorkflowType.APPOINTMENT_BOOKING.value
            params["preferred_date"] = "2026-06-20"

        result = await workflow_engine.start_workflow(workflow_type, uid, params)
        return AgentResult(
            agent=self.name,
            message=(
                f"Started workflow: {result['workflow_type']}\n"
                f"Status: {result['status']}\n"
                f"Tracking ID: {result['workflow_id']}\n"
                f"Track at: {result.get('tracking_url', 'N/A')}"
            ),
            metadata=result,
        )
