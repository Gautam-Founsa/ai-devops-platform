from pydantic import BaseModel, Field


class ClusterOverview(BaseModel):
    name: str
    provider: str
    region: str
    status: str
    nodes_ready: int
    nodes_total: int
    namespaces: int
    pods_running: int
    pods_pending: int
    pods_failed: int
    cpu_request_percent: float
    memory_request_percent: float


class PodSummary(BaseModel):
    name: str
    namespace: str
    workload: str
    status: str
    restarts: int
    cpu_millicores: int
    memory_mib: int
    age: str
    node: str
    reason: str | None = None


class ResourceRecommendation(BaseModel):
    target: str
    namespace: str
    recommendation: str
    current: str
    suggested: str
    confidence: float
    rationale: str


class CrashLoopAnalysisRequest(BaseModel):
    namespace: str = Field(default="default", max_length=160)
    pod_name: str = Field(min_length=1, max_length=240)


class CrashLoopAnalysisResponse(BaseModel):
    pod: PodSummary
    likely_causes: list[str]
    evidence: list[str]
    remediation_steps: list[str]


class YamlExplainRequest(BaseModel):
    yaml: str = Field(min_length=1, max_length=20000)


class YamlExplainResponse(BaseModel):
    kind: str
    name: str
    namespace: str
    summary: str
    risks: list[str]
    recommendations: list[str]


class ManifestGenerateRequest(BaseModel):
    app_name: str = Field(min_length=1, max_length=80)
    image: str = Field(min_length=1, max_length=240)
    namespace: str = Field(default="default", max_length=160)
    replicas: int = Field(default=2, ge=1, le=50)
    port: int = Field(default=8080, ge=1, le=65535)
    cpu_request: str = Field(default="100m", max_length=30)
    memory_request: str = Field(default="128Mi", max_length=30)


class ManifestGenerateResponse(BaseModel):
    yaml: str
    notes: list[str]

