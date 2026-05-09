"""phase 6 security scanner

Revision ID: 0004_phase6_security
Revises: 0003_phase3_kubernetes
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_phase6_security"
down_revision = "0003_phase3_kubernetes"
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "security_findings",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("scanner", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("cve_id", sa.String(length=80), nullable=True),
        sa.Column("package_name", sa.String(length=160), nullable=True),
        sa.Column("installed_version", sa.String(length=80), nullable=True),
        sa.Column("fixed_version", sa.String(length=80), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("metadata_json", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_security_findings_org_severity_status",
        "security_findings",
        ["organization_id", "severity", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_security_findings_org_severity_status", table_name="security_findings")
    op.drop_table("security_findings")

