from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LogIngestRequest(BaseModel):
    service_name: str = Field(min_length=1, max_length=160)
    environment: str = Field(default="production", max_length=80)
    level: str = Field(min_length=1, max_length=30)
    message: str = Field(min_length=1, max_length=8000)
    trace_id: str | None = Field(default=None, max_length=120)
    timestamp: datetime | None = None
    labels: dict = Field(default_factory=dict)


class LogEntryResponse(BaseModel):
    id: UUID
    service_name: str
    environment: str
    level: str
    message: str
    trace_id: str | None
    timestamp: datetime
    labels: dict
    score: float | None = None


class LogSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    service_name: str | None = Field(default=None, max_length=160)
    level: str | None = Field(default=None, max_length=30)
    limit: int = Field(default=10, ge=1, le=50)


class LogSearchResponse(BaseModel):
    query: str
    semantic: bool
    results: list[LogEntryResponse]

