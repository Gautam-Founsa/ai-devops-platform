from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SecurityScanFile(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=100000)


class SecurityScanRequest(BaseModel):
    repository: str | None = Field(default=None, max_length=240)
    files: list[SecurityScanFile] = Field(default_factory=list, max_length=30)
    include_trivy: bool = True
    include_semgrep: bool = True


class SecurityFindingResponse(BaseModel):
    id: UUID | None = None
    scanner: str
    category: str
    severity: str
    title: str
    description: str
    file_path: str | None = None
    line: int | None = None
    cve_id: str | None = None
    package_name: str | None = None
    installed_version: str | None = None
    fixed_version: str | None = None
    recommendation: str
    status: str = "open"
    metadata: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class SecurityToolStatus(BaseModel):
    name: str
    enabled: bool
    integrated: bool
    mode: str
    detail: str


class SecurityScanResponse(BaseModel):
    repository: str | None
    summary: dict[str, int]
    findings: list[SecurityFindingResponse]
    recommendations: list[str]
    tools: list[SecurityToolStatus]

