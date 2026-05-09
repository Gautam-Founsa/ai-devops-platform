from pydantic import BaseModel, Field


class CicdAnalyzeRequest(BaseModel):
    workflow_yaml: str = Field(min_length=1, max_length=50000)
    repository: str | None = Field(default=None, max_length=240)


class CicdFinding(BaseModel):
    severity: str
    category: str
    title: str
    detail: str
    recommendation: str


class WorkflowJobSummary(BaseModel):
    name: str
    runs_on: str
    steps: int
    uses_cache: bool
    uploads_artifacts: bool
    has_permissions: bool
    has_timeout: bool
    matrix: bool


class CicdAnalyzeResponse(BaseModel):
    workflow_name: str
    triggers: list[str]
    jobs: list[WorkflowJobSummary]
    findings: list[CicdFinding]
    caching_suggestions: list[str]
    parallelization_suggestions: list[str]
    security_best_practices: list[str]
    score: int


class CicdOptimizeRequest(BaseModel):
    workflow_yaml: str = Field(min_length=1, max_length=50000)
    goals: list[str] = Field(default_factory=list)


class CicdOptimizeResponse(BaseModel):
    optimized_workflow_yaml: str
    changes: list[str]
    analysis: CicdAnalyzeResponse

