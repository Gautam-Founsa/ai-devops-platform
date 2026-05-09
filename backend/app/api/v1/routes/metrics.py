from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.metrics import MetricsQueryResponse
from app.services.metrics import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/query", response_model=MetricsQueryResponse)
async def query_metrics(
    query: str = Query(default="rate(http_requests_total[5m])"),
    user: User = Depends(get_current_user),
) -> MetricsQueryResponse:
    del user
    points = await MetricsService().query(query)
    return MetricsQueryResponse(query=query, series=points)

