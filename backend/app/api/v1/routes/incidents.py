from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.schemas.incidents import (
    IncidentAnalyzeRequest,
    IncidentAnalyzeResponse,
    IncidentResponse,
)
from app.services.incidents import IncidentAnalyzerService

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[IncidentResponse]:
    return await IncidentAnalyzerService(db).list_incidents(user.organization_id)


@router.post("/analyze", response_model=IncidentAnalyzeResponse)
async def analyze_incident(
    payload: IncidentAnalyzeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentAnalyzeResponse:
    return await IncidentAnalyzerService(db).analyze(
        organization_id=user.organization_id,
        title=payload.title,
        query=payload.query,
        severity=payload.severity,
        limit=payload.limit,
        service_name=payload.service_name,
    )

