from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import LogEntry, LogsEmbedding
from app.schemas.logs import LogIngestRequest, LogEntryResponse
from app.services.vector_store import ChromaLogStore


class LogIntelligenceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.vector_store = ChromaLogStore()

    async def ingest(self, organization_id: UUID, payload: LogIngestRequest) -> LogEntryResponse:
        log = LogEntry(
            organization_id=organization_id,
            service_name=payload.service_name,
            environment=payload.environment,
            level=payload.level.upper(),
            message=payload.message,
            trace_id=payload.trace_id,
            timestamp=payload.timestamp or datetime.now(UTC),
            labels=payload.labels,
        )
        self.db.add(log)
        await self.db.flush()

        indexed = await self.vector_store.upsert_log(
            log.id,
            organization_id,
            payload.message,
            {
                "service_name": log.service_name,
                "environment": log.environment,
                "level": log.level,
                "trace_id": log.trace_id,
            },
        )
        self.db.add(
            LogsEmbedding(
                organization_id=organization_id,
                message=payload.message,
                embedding_ref=str(log.id) if indexed else "db-fallback",
                labels={
                    "service_name": log.service_name,
                    "environment": log.environment,
                    "level": log.level,
                    "indexed": indexed,
                },
            )
        )
        await self.db.commit()
        await self.db.refresh(log)
        return self._response(log)

    async def search(
        self,
        organization_id: UUID,
        query: str,
        limit: int,
        service_name: str | None = None,
        level: str | None = None,
    ) -> tuple[bool, list[LogEntryResponse]]:
        hits = await self.vector_store.search(organization_id, query, limit)
        if hits:
            hit_map = {UUID(hit.id): hit for hit in hits}
            result = await self.db.execute(
                select(LogEntry).where(
                    LogEntry.organization_id == organization_id,
                    LogEntry.id.in_(hit_map.keys()),
                )
            )
            logs = list(result.scalars().all())
            filtered = self._filter(logs, service_name, level)
            ordered = sorted(filtered, key=lambda log: hit_map[log.id].distance)
            return True, [
                self._response(log, score=round(1.0 / (1.0 + hit_map[log.id].distance), 4))
                for log in ordered[:limit]
            ]

        tokens = [token for token in query.split() if len(token) > 2][:8]
        predicates = [
            LogEntry.message.ilike(f"%{token}%")
            for token in tokens
        ] or [LogEntry.message.ilike(f"%{query}%")]
        predicates.extend(
            [
                LogEntry.service_name.ilike(f"%{query}%"),
                LogEntry.level.ilike(f"%{query}%"),
            ]
        )
        result = await self.db.execute(
            select(LogEntry)
            .where(
                LogEntry.organization_id == organization_id,
                or_(*predicates),
            )
            .order_by(LogEntry.timestamp.desc())
            .limit(limit * 2)
        )
        logs = self._filter(list(result.scalars().all()), service_name, level)
        return False, [self._response(log) for log in logs[:limit]]

    def _filter(
        self,
        logs: list[LogEntry],
        service_name: str | None,
        level: str | None,
    ) -> list[LogEntry]:
        return [
            log
            for log in logs
            if (service_name is None or log.service_name == service_name)
            and (level is None or log.level == level.upper())
        ]

    def _response(self, log: LogEntry, score: float | None = None) -> LogEntryResponse:
        return LogEntryResponse(
            id=log.id,
            service_name=log.service_name,
            environment=log.environment,
            level=log.level,
            message=log.message,
            trace_id=log.trace_id,
            timestamp=log.timestamp,
            labels=log.labels,
            score=score,
        )
