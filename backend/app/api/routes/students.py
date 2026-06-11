from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, DbSession, get_current_user, get_current_user_optional
from app.core.memory import DEMO_STUDENT_MEMORY
from app.core.rbac import UserRole, has_permission
from app.schemas import StudentProfileResponse
from app.services.audit import log_audit
from app.services.degree import degree_engine
from app.services.memory import load_student_memory

router = APIRouter()


@router.get("/demo", response_model=StudentProfileResponse)
async def get_demo_student(
    db: DbSession,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    if current_user is not None and not has_permission(current_user.role, "view_own_profile"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    if current_user is not None and current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo student profile is only available to student and admin roles",
        )

    memory = await load_student_memory(db, current_user.id if current_user else None)
    profile_id = UUID(memory.get("user_id", DEMO_STUDENT_MEMORY.user_id))

    await log_audit(
        db,
        user_id=current_user.id if current_user else None,
        action="student.profile_view",
        resource="students",
        details={"profile_id": str(profile_id)},
    )

    return StudentProfileResponse(
        id=profile_id,
        full_name=memory.get("full_name", ""),
        program=memory.get("program", ""),
        credits_earned=memory.get("credits_earned", 0),
        credits_required=memory.get("credits_required", 120),
        credits_remaining=memory.get("credits_remaining", 0),
        academic_standing=memory.get("academic_standing", "good"),
        student_type="undergraduate",
        career_interests=memory.get("career_interests", []),
        current_courses=memory.get("current_courses", []),
        upcoming_deadlines=memory.get("upcoming_deadlines", []),
    )


@router.get("/progress", response_model=dict)
async def get_student_progress(
    db: DbSession,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    if not has_permission(current_user.role, "view_own_profile"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    memory = await load_student_memory(db, current_user.id)
    completed_codes = [c.split()[0] for c in memory.get("completed_courses", []) if c]
    assessment = degree_engine.assess_graduation(
        program=memory.get("program", ""),
        credits_earned=memory.get("credits_earned", 0),
        completed_course_codes=completed_codes,
        academic_standing=memory.get("academic_standing", "good"),
    )
    roadmap = degree_engine.build_roadmap(
        program=memory.get("program", ""),
        credits_earned=memory.get("credits_earned", 0),
        completed_course_codes=completed_codes,
    )

    return {
        "profile": memory,
        "graduation": {
            "eligible": assessment.eligible,
            "summary": assessment.summary,
            "missing_core": assessment.missing_core,
            "credits_remaining": assessment.credits_remaining,
        },
        "roadmap": roadmap,
        "progress_percent": round(
            100 * memory.get("credits_earned", 0) / max(1, memory.get("credits_required", 120)),
            1,
        ),
    }
