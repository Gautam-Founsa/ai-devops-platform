from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.cicd import (
    CicdAnalyzeRequest,
    CicdAnalyzeResponse,
    CicdOptimizeRequest,
    CicdOptimizeResponse,
)
from app.services.cicd import CicdAnalyzerService

router = APIRouter(prefix="/cicd", tags=["cicd"])


@router.post("/analyze", response_model=CicdAnalyzeResponse)
async def analyze_workflow(
    payload: CicdAnalyzeRequest,
    user: User = Depends(get_current_user),
) -> CicdAnalyzeResponse:
    del user
    try:
        return CicdAnalyzerService().analyze(payload.workflow_yaml, payload.repository)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/optimize", response_model=CicdOptimizeResponse)
async def optimize_workflow(
    payload: CicdOptimizeRequest,
    user: User = Depends(get_current_user),
) -> CicdOptimizeResponse:
    del user
    try:
        return CicdAnalyzerService().optimize(payload.workflow_yaml, payload.goals)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

