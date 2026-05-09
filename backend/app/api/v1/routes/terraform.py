from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.terraform import (
    TerraformGenerateRequest,
    TerraformGenerateResponse,
    TerraformTemplateResponse,
    TerraformValidateRequest,
    TerraformValidateResponse,
)
from app.services.terraform import TerraformGeneratorService

router = APIRouter(prefix="/terraform", tags=["terraform"])


@router.get("/templates", response_model=list[TerraformTemplateResponse])
async def list_templates(user: User = Depends(get_current_user)) -> list[TerraformTemplateResponse]:
    del user
    return TerraformGeneratorService().templates()


@router.post("/generate", response_model=TerraformGenerateResponse)
async def generate_terraform(
    payload: TerraformGenerateRequest,
    user: User = Depends(get_current_user),
) -> TerraformGenerateResponse:
    del user
    return TerraformGeneratorService().generate(payload)


@router.post("/validate", response_model=TerraformValidateResponse)
async def validate_terraform(
    payload: TerraformValidateRequest,
    user: User = Depends(get_current_user),
) -> TerraformValidateResponse:
    del user
    return TerraformGeneratorService().validate_hcl(payload.hcl, payload.files)

