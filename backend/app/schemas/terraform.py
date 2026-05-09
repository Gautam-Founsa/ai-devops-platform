from pydantic import BaseModel, Field


class TerraformGenerateRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=2000)
    template: str = Field(default="ecs-rds-alb", pattern="^(ecs|rds|alb|ecs-rds-alb)$")
    app_name: str = Field(default="ai-devops-app", min_length=1, max_length=80)
    region: str = Field(default="us-east-1", max_length=40)
    environment: str = Field(default="prod", max_length=40)
    container_image: str = Field(default="public.ecr.aws/nginx/nginx:latest", max_length=240)


class TerraformValidationFinding(BaseModel):
    severity: str
    code: str
    message: str
    recommendation: str


class TerraformGenerateResponse(BaseModel):
    template: str
    files: dict[str, str]
    explanation: str
    security_best_practices: list[str]
    validation: list[TerraformValidationFinding]


class TerraformValidateRequest(BaseModel):
    files: dict[str, str] = Field(default_factory=dict)
    hcl: str | None = Field(default=None, max_length=50000)


class TerraformValidateResponse(BaseModel):
    valid: bool
    findings: list[TerraformValidationFinding]


class TerraformTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    resources: list[str]

