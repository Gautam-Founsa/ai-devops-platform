from pydantic import BaseModel


class CostBreakdownItem(BaseModel):
    service: str
    category: str
    monthly_cost: float
    change_percent: float
    owner: str


class CostTrendPoint(BaseModel):
    date: str
    amount: float


class CostRecommendationResponse(BaseModel):
    id: str
    category: str
    priority: str
    resource: str
    service: str
    current_monthly_cost: float
    estimated_monthly_savings: float
    title: str
    rationale: str
    action: str
    confidence: float


class CostSummaryResponse(BaseModel):
    currency: str
    month_to_date: float
    forecast_monthly: float
    previous_month: float
    potential_savings: float
    idle_spend: float
    rightsizing_savings: float
    breakdown: list[CostBreakdownItem]
    trend: list[CostTrendPoint]

