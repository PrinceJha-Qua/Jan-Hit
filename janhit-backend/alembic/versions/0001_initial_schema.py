"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("role", sa.String, default="field_worker"),
        sa.Column("district", sa.String, nullable=True),
    )

    op.create_table(
        "beneficiaries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("district", sa.String, nullable=False),
        sa.Column("occupation", sa.String, nullable=False),
        sa.Column("annual_income", sa.Integer, nullable=False),
        sa.Column("is_widow", sa.Boolean, default=False),
        sa.Column("is_farmer", sa.Boolean, default=False),
        sa.Column("has_disability", sa.Boolean, default=False),
        sa.Column("caste", sa.String, nullable=True),
        sa.Column("gender", sa.String, nullable=False),
    )

    op.create_table(
        "cases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("beneficiary_id", UUID(as_uuid=True), sa.ForeignKey("beneficiaries.id"), nullable=False),
        sa.Column("status", sa.String, default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("beneficiary_id", UUID(as_uuid=True), sa.ForeignKey("beneficiaries.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "schemes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("department", sa.String, nullable=False),
        sa.Column("benefit_amount", sa.String, nullable=False),
        sa.Column("min_age", sa.Integer, nullable=True),
        sa.Column("max_age", sa.Integer, nullable=True),
        sa.Column("max_annual_income", sa.Integer, nullable=True),
        sa.Column("requires_widow", sa.Boolean, nullable=True),
        sa.Column("requires_farmer", sa.Boolean, nullable=True),
        sa.Column("requires_disability", sa.Boolean, nullable=True),
        sa.Column("allowed_genders", ARRAY(sa.String), nullable=True),
        sa.Column("allowed_districts", ARRAY(sa.String), nullable=True),
        sa.Column("required_documents", ARRAY(sa.String), nullable=False),
        sa.Column("next_step_template", sa.String, nullable=False),
        sa.Column("why_eligible_template", sa.String, nullable=False),
    )

    op.create_table(
        "eligibility_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", UUID(as_uuid=True), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("scheme_id", UUID(as_uuid=True), sa.ForeignKey("schemes.id"), nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("why_eligible", sa.String, nullable=False),
        sa.Column("missing_documents", ARRAY(sa.String), nullable=True),
        sa.Column("next_step", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "action_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("status", sa.String, default="pending"),
        sa.Column("owner", sa.String, nullable=False),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("order_index", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "shareable_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("token", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String, nullable=False),
        sa.Column("entity_id", sa.String, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("details", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("shareable_links")
    op.drop_table("action_steps")
    op.drop_table("eligibility_results")
    op.drop_table("schemes")
    op.drop_table("assessments")
    op.drop_table("cases")
    op.drop_table("beneficiaries")
    op.drop_table("users")
