"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def id_column() -> sa.Column:
    return sa.Column("id", UUID, nullable=False)


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        *timestamps(),
        id_column(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    op.create_table(
        "users",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "clusters",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("region", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "services",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("environment", sa.String(length=80), nullable=False),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("owner_team", sa.String(length=160), nullable=True),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "incidents",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alerts",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("service_id", UUID, nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "deployments",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("service_id", UUID, nullable=False),
        sa.Column("version", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversations",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "messages",
        sa.Column("conversation_id", UUID, nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )

    op.create_table(
        "metrics_snapshots",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("service_id", UUID, nullable=True),
        sa.Column("metric_name", sa.String(length=160), nullable=False),
        sa.Column("value", sa.Numeric(14, 4), nullable=False),
        sa.Column("labels", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_metrics_snapshots_org_metric_created",
        "metrics_snapshots",
        ["organization_id", "metric_name", "created_at"],
    )

    op.create_table(
        "logs_embeddings",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("service_id", UUID, nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("embedding_ref", sa.String(length=255), nullable=False),
        sa.Column("labels", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "recommendations",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=True),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "runbooks",
        sa.Column("organization_id", UUID, nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tags", JSONB, nullable=False),
        *timestamps(),
        id_column(),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("runbooks")
    op.drop_table("audit_logs")
    op.drop_table("recommendations")
    op.drop_table("logs_embeddings")
    op.drop_index("ix_metrics_snapshots_org_metric_created", table_name="metrics_snapshots")
    op.drop_table("metrics_snapshots")
    op.drop_index("ix_messages_conversation_created", table_name="messages")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("deployments")
    op.drop_table("alerts")
    op.drop_table("incidents")
    op.drop_table("services")
    op.drop_table("clusters")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")
