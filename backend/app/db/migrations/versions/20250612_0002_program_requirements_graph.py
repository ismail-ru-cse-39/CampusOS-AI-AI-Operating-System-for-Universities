"""Add program_requirements and graph_edges tables.

Revision ID: 20250612_0002
Revises: 20250612_0001
Create Date: 2025-06-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20250612_0002"
down_revision: Union[str, None] = "20250612_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "program_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_name", sa.String(length=255), nullable=False),
        sa.Column("total_credits", sa.Integer(), nullable=False),
        sa.Column("min_gpa", sa.Float(), nullable=False),
        sa.Column("core_courses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("elective_credits", sa.Integer(), nullable=False),
        sa.Column("capstone_course", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "graph_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("relationship", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("graph_edges")
    op.drop_table("program_requirements")
