from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import User
from app.schemas.security import SecurityFindingResponse, SecurityScanRequest, SecurityScanResponse
from app.services.security import SecurityScannerService

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/scan", response_model=SecurityScanResponse)
async def scan_security(
    payload: SecurityScanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityScanResponse:
    return await SecurityScannerService(db).scan(
        organization_id=user.organization_id,
        repository=payload.repository,
        files=payload.files,
        include_trivy=payload.include_trivy,
        include_semgrep=payload.include_semgrep,
    )


@router.get("/findings", response_model=list[SecurityFindingResponse])
async def list_findings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SecurityFindingResponse]:
    return await SecurityScannerService(db).findings(user.organization_id)

