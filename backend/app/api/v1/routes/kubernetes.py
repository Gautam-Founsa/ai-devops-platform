from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.kubernetes import (
    ClusterOverview,
    CrashLoopAnalysisRequest,
    CrashLoopAnalysisResponse,
    ManifestGenerateRequest,
    ManifestGenerateResponse,
    PodSummary,
    ResourceRecommendation,
    YamlExplainRequest,
    YamlExplainResponse,
)
from app.services.kubernetes import KubernetesIntelligenceService

router = APIRouter(prefix="/k8s", tags=["kubernetes"])


@router.get("/overview", response_model=ClusterOverview)
async def cluster_overview(user: User = Depends(get_current_user)) -> ClusterOverview:
    del user
    return KubernetesIntelligenceService().cluster_overview()


@router.get("/pods", response_model=list[PodSummary])
async def list_pods(
    namespace: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> list[PodSummary]:
    del user
    return KubernetesIntelligenceService().pods(namespace)


@router.post("/crashloop/analyze", response_model=CrashLoopAnalysisResponse)
async def analyze_crash_loop(
    payload: CrashLoopAnalysisRequest,
    user: User = Depends(get_current_user),
) -> CrashLoopAnalysisResponse:
    del user
    return KubernetesIntelligenceService().analyze_crash_loop(payload.namespace, payload.pod_name)


@router.get("/recommendations", response_model=list[ResourceRecommendation])
async def resource_recommendations(
    user: User = Depends(get_current_user),
) -> list[ResourceRecommendation]:
    del user
    return KubernetesIntelligenceService().recommendations()


@router.post("/explain", response_model=YamlExplainResponse)
async def explain_yaml(
    payload: YamlExplainRequest,
    user: User = Depends(get_current_user),
) -> YamlExplainResponse:
    del user
    try:
        return KubernetesIntelligenceService().explain_yaml(payload.yaml)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/generate", response_model=ManifestGenerateResponse)
async def generate_manifest(
    payload: ManifestGenerateRequest,
    user: User = Depends(get_current_user),
) -> ManifestGenerateResponse:
    del user
    return KubernetesIntelligenceService().generate_manifest(payload)

