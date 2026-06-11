import asyncio
from uuid import UUID

from app.services.degree import degree_engine
from app.services.ingestion import chunk_text
from app.services.llm import _deterministic_embedding, llm_service
from app.services.retention import retention_service
from app.services.workflow_engine import WorkflowType, workflow_engine


def test_degree_graduation_assessment():
    result = degree_engine.assess_graduation(
        program="BSc Computer Science",
        credits_earned=120,
        completed_course_codes=["CS101", "CS201", "CS301", "CS350", "CS401", "MATH101", "MATH301"],
        academic_standing="good",
    )
    assert result.eligible is True
    assert result.credits_remaining == 0


def test_degree_roadmap_with_career_path():
    roadmap = degree_engine.build_roadmap(
        program="BSc Computer Science",
        credits_earned=84,
        completed_course_codes=["CS101", "CS201", "CS301"],
        career_goal="ai engineer",
    )
    assert roadmap["credits_remaining"] == 36
    assert roadmap["career_pathway"] is not None
    assert len(roadmap["semesters"]) >= 1


def test_chunk_text_overlap():
    text = "word " * 200
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1


def test_mock_embeddings_deterministic():
    a = asyncio.run(llm_service.embed("hello world"))
    b = asyncio.run(llm_service.embed("hello world"))
    c = asyncio.run(llm_service.embed("different text"))
    assert a == b
    assert a != c
    assert len(a) == 1536


def test_retention_scoring():
    scores = retention_service.score_all()
    assert len(scores) >= 1
    critical = retention_service.at_risk_students("high")
    assert all(s.risk_level in ("high", "critical") for s in critical)


def test_workflow_engine_transcript():
    uid = UUID("00000000-0000-4000-8000-000000000001")
    result = asyncio.run(
        workflow_engine.start_workflow(
            WorkflowType.TRANSCRIPT_REQUEST.value, uid, {"student_verified": True}
        )
    )
    assert result["status"] == "completed"
    assert result["workflow_id"] is not None

    status = asyncio.run(workflow_engine.get_status(UUID(result["workflow_id"])))
    assert status["status"] == "completed"


def test_deterministic_embedding_norm():
    emb = _deterministic_embedding("test")
    norm = sum(x * x for x in emb) ** 0.5
    assert abs(norm - 1.0) < 0.01
