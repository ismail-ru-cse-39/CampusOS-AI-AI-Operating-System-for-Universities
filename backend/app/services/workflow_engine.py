from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, Enum):
    TRANSCRIPT_REQUEST = "transcript_request"
    ENROLLMENT_VERIFICATION = "enrollment_verification"
    APPOINTMENT_BOOKING = "appointment_booking"


WORKFLOW_STEPS: dict[str, list[str]] = {
    WorkflowType.TRANSCRIPT_REQUEST.value: [
        "validate_student",
        "check_holds",
        "generate_transcript",
        "notify_student",
    ],
    WorkflowType.ENROLLMENT_VERIFICATION.value: [
        "validate_student",
        "verify_enrollment",
        "generate_letter",
        "notify_student",
    ],
    WorkflowType.APPOINTMENT_BOOKING.value: [
        "validate_student",
        "check_availability",
        "book_slot",
        "send_confirmation",
    ],
}


@dataclass
class WorkflowInstance:
    workflow_id: UUID
    workflow_type: str
    user_id: UUID
    status: WorkflowStatus
    current_step: int
    steps: list[str]
    params: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class WorkflowEngine:
    """In-memory workflow state machine (Redis/Celery worker in production)."""

    def __init__(self) -> None:
        self._workflows: dict[UUID, WorkflowInstance] = {}

    async def start_workflow(
        self,
        workflow_type: str,
        user_id: UUID,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if workflow_type not in WORKFLOW_STEPS:
            return {
                "workflow_id": None,
                "status": WorkflowStatus.FAILED.value,
                "message": f"Unknown workflow type: {workflow_type}",
            }

        workflow_id = uuid4()
        steps = WORKFLOW_STEPS[workflow_type]
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            user_id=user_id,
            status=WorkflowStatus.PENDING,
            current_step=0,
            steps=steps,
            params=params,
        )
        self._workflows[workflow_id] = instance

        from app.workers import enqueue_task

        enqueue_task(
            f"workflow_{workflow_type}",
            {"workflow_id": str(workflow_id), "user_id": str(user_id), "params": params},
        )
        await self._advance(instance)
        return self._to_response(instance)

    async def _advance(self, instance: WorkflowInstance) -> None:
        instance.status = WorkflowStatus.RUNNING
        instance.updated_at = datetime.now(timezone.utc)

        while instance.current_step < len(instance.steps):
            step = instance.steps[instance.current_step]
            ok = await self._execute_step(instance, step)
            if not ok:
                instance.status = WorkflowStatus.FAILED
                instance.updated_at = datetime.now(timezone.utc)
                return
            instance.current_step += 1
            instance.updated_at = datetime.now(timezone.utc)

        instance.status = WorkflowStatus.COMPLETED
        instance.result = {
            "message": f"Workflow '{instance.workflow_type}' completed successfully.",
            "tracking_url": f"/api/v1/workflows/{instance.workflow_id}",
        }

    async def _execute_step(self, instance: WorkflowInstance, step: str) -> bool:
        # Simulated step execution — worker would run async jobs in production
        if step == "validate_student" and not instance.params.get("student_verified", True):
            instance.error = "Student validation failed"
            return False
        if step == "check_holds" and instance.params.get("financial_hold"):
            instance.error = "Financial hold prevents processing"
            return False
        if step == "check_availability" and not instance.params.get("preferred_date"):
            instance.error = "Preferred date required for appointment booking"
            return False
        return True

    async def get_status(self, workflow_id: UUID) -> dict[str, Any]:
        instance = self._workflows.get(workflow_id)
        if instance is None:
            return {
                "workflow_id": str(workflow_id),
                "status": WorkflowStatus.FAILED.value,
                "message": "Workflow not found",
            }
        return self._to_response(instance)

    async def cancel(self, workflow_id: UUID) -> dict[str, Any]:
        instance = self._workflows.get(workflow_id)
        if instance is None:
            return {"workflow_id": str(workflow_id), "status": "not_found"}
        if instance.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
            return self._to_response(instance)
        instance.status = WorkflowStatus.CANCELLED
        instance.updated_at = datetime.now(timezone.utc)
        return self._to_response(instance)

    def _to_response(self, instance: WorkflowInstance) -> dict[str, Any]:
        current = (
            instance.steps[instance.current_step]
            if instance.current_step < len(instance.steps)
            else "done"
        )
        return {
            "workflow_id": str(instance.workflow_id),
            "workflow_type": instance.workflow_type,
            "status": instance.status.value,
            "current_step": current,
            "step_index": instance.current_step,
            "total_steps": len(instance.steps),
            "message": instance.error or instance.result.get("message", "In progress"),
            "tracking_url": f"/api/v1/workflows/{instance.workflow_id}",
            "params": instance.params,
            "result": instance.result,
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
        }


workflow_engine = WorkflowEngine()
