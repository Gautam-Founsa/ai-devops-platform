from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Incident, IncidentEvent
from app.schemas.incidents import (
    IncidentAnalyzeResponse,
    IncidentEventResponse,
    IncidentResponse,
)
from app.schemas.logs import LogEntryResponse
from app.services.logs import LogIntelligenceService


class IncidentAnalyzerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.logs = LogIntelligenceService(db)

    async def list_incidents(self, organization_id: UUID) -> list[IncidentResponse]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.organization_id == organization_id)
            .order_by(Incident.created_at.desc())
            .limit(50)
        )
        return [self._incident_response(incident) for incident in result.scalars().all()]

    async def analyze(
        self,
        organization_id: UUID,
        title: str,
        query: str,
        severity: str,
        limit: int,
        service_name: str | None,
    ) -> IncidentAnalyzeResponse:
        _, evidence_logs = await self.logs.search(
            organization_id=organization_id,
            query=query,
            limit=limit,
            service_name=service_name,
        )

        suspected_root_cause = self._root_cause(evidence_logs, query)
        summary = (
            f"Analyzed {len(evidence_logs)} relevant log events. "
            f"Likely cause: {suspected_root_cause}"
        )
        incident = Incident(
            organization_id=organization_id,
            title=title,
            severity=severity,
            status="open",
            summary=summary,
        )
        self.db.add(incident)
        await self.db.flush()

        events = self._build_events(incident.id, organization_id, evidence_logs)
        for event in events:
            self.db.add(event)
        await self.db.commit()
        await self.db.refresh(incident)

        return IncidentAnalyzeResponse(
            incident=self._incident_response(incident),
            timeline=[self._event_response(event) for event in events],
            suspected_root_cause=suspected_root_cause,
            recommended_actions=self._recommendations(evidence_logs),
            evidence_logs=evidence_logs,
        )

    def _build_events(
        self,
        incident_id: UUID,
        organization_id: UUID,
        logs: list[LogEntryResponse],
    ) -> list[IncidentEvent]:
        if not logs:
            return [
                IncidentEvent(
                    incident_id=incident_id,
                    organization_id=organization_id,
                    event_type="analysis",
                    title="No matching evidence found",
                    description="The analyzer could not find logs matching the investigation query.",
                    occurred_at=datetime.now(UTC),
                    evidence={},
                )
            ]

        ordered = sorted(logs, key=lambda log: log.timestamp)
        events: list[IncidentEvent] = []
        for index, log in enumerate(ordered[:12], start=1):
            event_type = "error" if log.level in {"ERROR", "FATAL", "CRITICAL"} else "signal"
            events.append(
                IncidentEvent(
                    incident_id=incident_id,
                    organization_id=organization_id,
                    event_type=event_type,
                    title=f"{index}. {log.level} from {log.service_name}",
                    description=log.message,
                    occurred_at=log.timestamp,
                    evidence={
                        "log_id": str(log.id),
                        "trace_id": log.trace_id,
                        "score": log.score,
                        "labels": log.labels,
                    },
                )
            )
        return events

    def _root_cause(self, logs: list[LogEntryResponse], query: str) -> str:
        messages = " ".join(log.message.lower() for log in logs)
        if any(term in messages for term in ["timeout", "deadline", "latency", "slow"]):
            return "downstream latency or timeout pressure is visible in the correlated logs"
        if any(term in messages for term in ["connection refused", "connect", "unavailable"]):
            return "dependency connectivity failures are the strongest signal"
        if any(term in messages for term in ["oom", "memory", "killed"]):
            return "resource exhaustion, especially memory pressure, is the strongest signal"
        if any(term in messages for term in ["exception", "traceback", "panic", "error"]):
            return "application errors increased around the investigation window"
        return f"insufficient evidence for a single root cause; continue investigating `{query}`"

    def _recommendations(self, logs: list[LogEntryResponse]) -> list[str]:
        services = sorted({log.service_name for log in logs})
        service_text = ", ".join(services) if services else "the affected services"
        return [
            f"Inspect recent deploys and config changes for {service_text}.",
            "Compare error-rate, latency, CPU, memory, and restart metrics across the same window.",
            "Follow shared trace IDs from the evidence logs to confirm the request path.",
        ]

    def _incident_response(self, incident: Incident) -> IncidentResponse:
        return IncidentResponse(
            id=incident.id,
            title=incident.title,
            severity=incident.severity,
            status=incident.status,
            summary=incident.summary,
            created_at=incident.created_at,
        )

    def _event_response(self, event: IncidentEvent) -> IncidentEventResponse:
        return IncidentEventResponse(
            id=event.id,
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            occurred_at=event.occurred_at,
            evidence=event.evidence,
        )

