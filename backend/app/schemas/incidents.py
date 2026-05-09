from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.logs import LogEntryResponse


class IncidentResponse(BaseModel):
    id: UUID
    title: str
    severity: str
    status: str
    summary: str | None
    created_at: datetime


class IncidentEventResponse(BaseModel):
    id: UUID
    event_type: str
    title: str
    description: str
    occurred_at: datetime
    evidence: dict


class IncidentAnalyzeRequest(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    query: str = Field(min_length=3, max_length=1000)
    service_name: str | None = Field(default=None, max_length=160)
    severity: str = Field(default="sev2", max_length=40)
    limit: int = Field(default=12, ge=3, le=50)


class IncidentAnalyzeResponse(BaseModel):
    incident: IncidentResponse
    timeline: list[IncidentEventResponse]
    suspected_root_cause: str
    recommended_actions: list[str]
    evidence_logs: list[LogEntryResponse]

