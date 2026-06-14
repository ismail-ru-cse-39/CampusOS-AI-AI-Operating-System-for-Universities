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
    language: Optional[str] = None
    university_slug: Optional[str] = None
    plan: Optional[str] = None


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
    current_courses: List[str] = []
    upcoming_deadlines: List[Dict[str, Any]] = []


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    category: str
    source_url: Optional[str]
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    title: str
    chunks_created: int
    message: str


class WorkflowResponse(BaseModel):
    workflow_id: Optional[str]
    workflow_type: str
    status: str
    message: str
    tracking_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ExecutiveMetricsResponse(BaseModel):
    metrics: Dict[str, Any]
    department_performance: List[Dict[str, Any]]
    retention_trends: List[Dict[str, Any]]


class WeeklyReportResponse(BaseModel):
    title: str
    period: str
    summary: str
    highlights: List[str]
    recommendations: List[str]


class TenantConfigResponse(BaseModel):
    slug: str
    name: str
    primary_color: str
    logo_url: Optional[str]
    plan: str
    features: Dict[str, bool]
    theme_css_vars: Dict[str, str]


class GraphQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    pattern: str


class NotificationResponse(BaseModel):
    id: UUID
    channel: str
    subject: str
    body: str
    status: str
