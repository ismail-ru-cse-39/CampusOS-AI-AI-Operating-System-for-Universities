from uuid import UUID

from fastapi import APIRouter

from app.core.memory import DEMO_STUDENT_MEMORY
from app.schemas import StudentProfileResponse

router = APIRouter()


@router.get("/demo", response_model=StudentProfileResponse)
async def get_demo_student():
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
