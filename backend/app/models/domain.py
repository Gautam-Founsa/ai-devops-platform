from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="admin", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization: Mapped[Organization] = relationship(back_populates="users")


class Cluster(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "clusters"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="unknown", nullable=False)


class Service(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "services"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    environment: Mapped[str] = mapped_column(String(80), nullable=False)
    repository_url: Mapped[str | None] = mapped_column(String(500))
    owner_team: Mapped[str | None] = mapped_column(String(160))


class Incident(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="open", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="firing", nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Deployment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "deployments"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    service_id: Mapped[UUID] = mapped_column(ForeignKey("services.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")


class Message(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class MetricsSnapshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "metrics_snapshots"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"))
    metric_name: Mapped[str] = mapped_column(String(160), nullable=False)
    value: Mapped[Numeric] = mapped_column(Numeric(14, 4), nullable=False)
    labels: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class LogsEmbedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "logs_embeddings"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    labels: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class LogEntry(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "log_entries"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    service_name: Mapped[str] = mapped_column(String(160), nullable=False)
    environment: Mapped[str] = mapped_column(String(80), default="production", nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(120))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    labels: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class IncidentEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incident_events"

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class KubernetesResourceSnapshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "kubernetes_resource_snapshots"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    cluster_id: Mapped[UUID | None] = mapped_column(ForeignKey("clusters.id"))
    namespace: Mapped[str] = mapped_column(String(160), nullable=False)
    kind: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    signals: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Recommendation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "recommendations"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="open", nullable=False)


class AuditLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(120))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Runbook(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "runbooks"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)


Index(
    "ix_metrics_snapshots_org_metric_created",
    MetricsSnapshot.organization_id,
    MetricsSnapshot.metric_name,
    MetricsSnapshot.created_at,
)
Index("ix_messages_conversation_created", Message.conversation_id, Message.created_at)
Index("ix_log_entries_org_timestamp", LogEntry.organization_id, LogEntry.timestamp)
Index("ix_log_entries_org_service_level", LogEntry.organization_id, LogEntry.service_name, LogEntry.level)
Index("ix_incident_events_incident_occurred", IncidentEvent.incident_id, IncidentEvent.occurred_at)
Index(
    "ix_kubernetes_resource_snapshots_org_kind_namespace",
    KubernetesResourceSnapshot.organization_id,
    KubernetesResourceSnapshot.kind,
    KubernetesResourceSnapshot.namespace,
)
