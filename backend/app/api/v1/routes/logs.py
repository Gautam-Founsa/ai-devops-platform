from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.schemas.logs import (
    LogEntryResponse,
    LogIngestRequest,
    LogSearchRequest,
    LogSearchResponse,
)
from app.services.logs import LogIntelligenceService

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/ingest", response_model=LogEntryResponse)
async def ingest_log(
    payload: LogIngestRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogEntryResponse:
    return await LogIntelligenceService(db).ingest(user.organization_id, payload)


@router.post("/search", response_model=LogSearchResponse)
async def search_logs(
    payload: LogSearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogSearchResponse:
    semantic, results = await LogIntelligenceService(db).search(
        organization_id=user.organization_id,
        query=payload.query,
        limit=payload.limit,
        service_name=payload.service_name,
        level=payload.level,
    )
    return LogSearchResponse(query=payload.query, semantic=semantic, results=results)

