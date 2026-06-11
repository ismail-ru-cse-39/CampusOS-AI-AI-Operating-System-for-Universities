#!/usr/bin/env python3
"""Seed Demo University with sample users, courses, and policy documents."""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Allow running from repo root, backend dir, or Docker (/scripts + /app)
BACKEND_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "backend",
    Path("/app"),
    Path(__file__).resolve().parent.parent,
]
for candidate in BACKEND_CANDIDATES:
    if (candidate / "app" / "main.py").exists():
        sys.path.insert(0, str(candidate))
        break

from sqlalchemy import select

from app.db.session import Base, async_session, engine, init_db
from app.models import (
    Course,
    Document,
    Enrollment,
    StudentProfile,
    University,
    User,
)

DEMO_UNIVERSITY_ID = UUID("00000000-0000-4000-8000-000000000010")

COURSES = [
    ("CS101", "Intro to Programming", 3, "Computer Science"),
    ("CS201", "Data Structures", 3, "Computer Science"),
    ("CS301", "Algorithms", 3, "Computer Science"),
    ("CS350", "Databases", 3, "Computer Science"),
    ("CS401", "Machine Learning", 3, "Computer Science"),
    ("MATH101", "Calculus I", 4, "Mathematics"),
    ("MATH201", "Calculus II", 4, "Mathematics"),
    ("MATH301", "Statistics", 3, "Mathematics"),
    ("ENG101", "Academic Writing", 3, "English"),
    ("PHYS201", "Physics I", 4, "Physics"),
]

DOCUMENTS = [
    (
        "Student Registration Policy 2026",
        "policy",
        "Registration for Fall 2026 opens August 15. Late registration incurs a $50 fee.",
    ),
    (
        "Graduation Requirements Handbook",
        "handbook",
        "120 credits required with minimum GPA 2.0. Apply one semester in advance.",
    ),
    (
        "Scholarship Application Guide",
        "guide",
        "Applications open March 1. Minimum GPA 3.0 for merit scholarships.",
    ),
    (
        "Department Transfer Policy",
        "policy",
        "Internal transfers require GPA 2.5 and first year completion.",
    ),
    (
        "International Student Visa Guide",
        "guide",
        "F-1 students must maintain 12+ credits and valid visa status.",
    ),
]

STUDENTS = [
    {
        "id": UUID("00000000-0000-4000-8000-000000000001"),
        "email": "alex.johnson@demo.edu",
        "name": "Alex Johnson",
        "type": "undergraduate",
        "program": "BSc Computer Science",
        "credits_earned": 84,
        "interests": ["AI Engineer", "Machine Learning"],
    },
    {
        "id": UUID("00000000-0000-4000-8000-000000000002"),
        "email": "maria.garcia@demo.edu",
        "name": "Maria Garcia",
        "type": "postgraduate",
        "program": "MSc Data Science",
        "credits_earned": 24,
        "interests": ["Data Analyst", "Research"],
    },
    {
        "id": UUID("00000000-0000-4000-8000-000000000003"),
        "email": "wei.zhang@demo.edu",
        "name": "Wei Zhang",
        "type": "international",
        "program": "BSc Engineering",
        "credits_earned": 45,
        "interests": ["Robotics", "Automation"],
    },
]

OTHER_USERS = [
    (UUID("00000000-0000-4000-8000-000000000020"), "prof.smith@demo.edu", "Dr. Jane Smith", "faculty"),
    (UUID("00000000-0000-4000-8000-000000000021"), "admin@demo.edu", "Admin User", "admin"),
]


async def seed() -> None:
    await init_db()

    async with async_session() as session:
        existing = await session.scalar(
            select(University).where(University.slug == "demo-university")
        )
        if existing:
            print("Demo University already seeded. Skipping.")
            return

        university = University(
            id=DEMO_UNIVERSITY_ID,
            name="Demo University",
            slug="demo-university",
        )
        session.add(university)

        course_objects: list[Course] = []
        for code, title, credits, dept in COURSES:
            course = Course(
                university_id=DEMO_UNIVERSITY_ID,
                code=code,
                title=title,
                credits=credits,
                department=dept,
            )
            session.add(course)
            course_objects.append(course)

        for title, category, content in DOCUMENTS:
            session.add(
                Document(
                    university_id=DEMO_UNIVERSITY_ID,
                    title=title,
                    category=category,
                    source_url=f"https://demo-university.edu/docs/{title.lower().replace(' ', '-')}",
                    content=content,
                )
            )

        for student in STUDENTS:
            user = User(
                id=student["id"],
                university_id=DEMO_UNIVERSITY_ID,
                email=student["email"],
                full_name=student["name"],
                role="student",
            )
            session.add(user)
            session.add(
                StudentProfile(
                    user_id=student["id"],
                    program=student["program"],
                    credits_earned=student["credits_earned"],
                    credits_required=120 if student["type"] != "postgraduate" else 36,
                    academic_standing="good",
                    student_type=student["type"],
                    career_interests=student["interests"],
                )
            )

        for uid, email, name, role in OTHER_USERS:
            session.add(
                User(
                    id=uid,
                    university_id=DEMO_UNIVERSITY_ID,
                    email=email,
                    full_name=name,
                    role=role,
                )
            )

        # Enroll Alex in current courses
        alex_id = STUDENTS[0]["id"]
        for code in ["CS401", "CS350", "MATH301"]:
            course = next(c for c in course_objects if c.code == code)
            session.add(
                Enrollment(
                    student_id=alex_id,
                    course_id=course.id,
                    status="enrolled",
                    semester="2026-Spring",
                )
            )

        await session.commit()
        print("Demo University seeded successfully.")
        print(f"  - 1 university, {len(COURSES)} courses, {len(DOCUMENTS)} documents")
        print(f"  - {len(STUDENTS)} students, {len(OTHER_USERS)} staff users")


if __name__ == "__main__":
    asyncio.run(seed())
