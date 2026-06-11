from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    environment: str
    agents_registered: int


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    user_role: str = "student"
    user_id: Optional[str] = None
    conversation_id: Optional[UUID] = None


class Citation(BaseModel):
    document_title: str
    source_url: Optional[str] = None
    excerpt: str


class ChatResponse(BaseModel):
    agent: str
    message: str
    citations: List[Citation] = []
    metadata: Dict[str, Any] = {}


class StudentProfileResponse(BaseModel):
    id: UUID
    full_name: str
    program: str
    credits_earned: int
    credits_required: int
    credits_remaining: int
    academic_standing: str
    student_type: str
    career_interests: List[str]


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    category: str
    source_url: Optional[str]
    created_at: datetime
