from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.cost import CostRecommendationResponse, CostSummaryResponse
from app.services.cost import CostOptimizationService

router = APIRouter(prefix="/cost", tags=["cost"])


@router.get("/recommendations", response_model=list[CostRecommendationResponse])
async def cost_recommendations(
    user: User = Depends(get_current_user),
) -> list[CostRecommendationResponse]:
    del user
    return CostOptimizationService().recommendations()


@router.get("/summary", response_model=CostSummaryResponse)
async def cost_summary(user: User = Depends(get_current_user)) -> CostSummaryResponse:
    del user
    return CostOptimizationService().summary()

