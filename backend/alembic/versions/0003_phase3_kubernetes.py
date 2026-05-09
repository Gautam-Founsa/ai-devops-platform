"""phase 3 kubernetes intelligence

Revision ID: 0003_phase3_kubernetes
Revises: 0002_phase2_logs_incidents
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_phase3_kubernetes"
down_revision = "0002_phase2_logs_incidents"
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "kubernetes_resource_snapshots",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("cluster_id", UUID, nullable=True),
        sa.Column("namespace", sa.String(length=160), nullable=False),
        sa.Column("kind", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("manifest", JSONB, nullable=False),
        sa.Column("signals", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["clusters.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_kubernetes_resource_snapshots_org_kind_namespace",
        "kubernetes_resource_snapshots",
        ["organization_id", "kind", "namespace"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_kubernetes_resource_snapshots_org_kind_namespace",
        table_name="kubernetes_resource_snapshots",
    )
    op.drop_table("kubernetes_resource_snapshots")
