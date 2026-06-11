from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.memory import DEMO_STUDENT_MEMORY, StudentMemory


async def load_student_memory(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
) -> dict[str, Any]:
    """Load student context from DB; falls back to demo memory when unavailable."""
    if user_id is None:
        return DEMO_STUDENT_MEMORY.to_context()

    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.models import Enrollment, User

        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.student_profile),
                selectinload(User.enrollments).selectinload(Enrollment.course),
            )
        )
        user = result.scalar_one_or_none()
        if user is None or user.student_profile is None:
            return DEMO_STUDENT_MEMORY.to_context()

        profile = user.student_profile
        current = [
            f"{e.course.code} {e.course.title}"
            for e in user.enrollments
            if e.status == "enrolled"
        ]
        completed = [
            f"{e.course.code} {e.course.title}"
            for e in user.enrollments
            if e.status in ("completed", "passed")
        ]

        memory = StudentMemory(
            user_id=str(user.id),
            full_name=user.full_name,
            program=profile.program,
            credits_earned=profile.credits_earned,
            credits_required=profile.credits_required,
            current_courses=current,
            completed_courses=completed,
            academic_standing=profile.academic_standing,
            career_interests=list(profile.career_interests or []),
        )
        return memory.to_context()
    except Exception:
        return DEMO_STUDENT_MEMORY.to_context()
