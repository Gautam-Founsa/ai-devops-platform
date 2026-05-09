"""phase 2 logs and incident timeline

Revision ID: 0002_phase2_logs_incidents
Revises: 0001_initial_schema
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_phase2_logs_incidents"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "log_entries",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("service_name", sa.String(length=160), nullable=False),
        sa.Column("environment", sa.String(length=80), nullable=False),
        sa.Column("level", sa.String(length=30), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("trace_id", sa.String(length=120), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("labels", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_log_entries_org_timestamp", "log_entries", ["organization_id", "timestamp"])
    op.create_index(
        "ix_log_entries_org_service_level",
        "log_entries",
        ["organization_id", "service_name", "level"],
    )

    op.create_table(
        "incident_events",
        sa.Column("incident_id", UUID, nullable=False),
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", UUID, nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_incident_events_incident_occurred",
        "incident_events",
        ["incident_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_incident_events_incident_occurred", table_name="incident_events")
    op.drop_table("incident_events")
    op.drop_index("ix_log_entries_org_service_level", table_name="log_entries")
    op.drop_index("ix_log_entries_org_timestamp", table_name="log_entries")
    op.drop_table("log_entries")
