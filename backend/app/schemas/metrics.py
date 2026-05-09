from pydantic import BaseModel


class MetricPoint(BaseModel):
    timestamp: str
    value: float


class MetricsQueryResponse(BaseModel):
    query: str
    series: list[MetricPoint]

