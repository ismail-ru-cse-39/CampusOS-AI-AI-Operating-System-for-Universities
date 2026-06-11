from __future__ import annotations

from typing import Any, Optional

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, get_current_user_optional
from app.core.memory import DEMO_STUDENT_MEMORY
from app.core.rbac import UserRole, has_permission
from app.schemas import StudentProfileResponse

router = APIRouter()


@router.get("/demo", response_model=StudentProfileResponse)
async def get_demo_student(
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    if current_user is not None and not has_permission(current_user.role, "view_own_profile"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    if current_user is not None and current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo student profile is only available to student and admin roles",
        )

    memory = DEMO_STUDENT_MEMORY
    return StudentProfileResponse(
        id=UUID(memory.user_id),
        full_name=memory.full_name,
        program=memory.program,
        credits_earned=memory.credits_earned,
        credits_required=memory.credits_required,
        credits_remaining=max(0, memory.credits_required - memory.credits_earned),
        academic_standing=memory.academic_standing,
        student_type="undergraduate",
        career_interests=memory.career_interests,
    )
