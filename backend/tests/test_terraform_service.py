from app.schemas.terraform import TerraformGenerateRequest
from app.services.terraform import TerraformGeneratorService


def test_generates_ecs_rds_alb_template() -> None:
    response = TerraformGeneratorService().generate(
        TerraformGenerateRequest(
            prompt="Production ECS service with RDS and an ALB",
            template="ecs-rds-alb",
            app_name="checkout-api",
        )
    )
    assert "ecs.tf" in response.files
    assert "rds.tf" in response.files
    assert "alb.tf" in response.files
    assert response.validation == []


def test_validation_flags_public_database() -> None:
    response = TerraformGeneratorService().validate(
        {
            "main.tf": """
            resource "aws_security_group" "db" {
              ingress {
                from_port   = 5432
                cidr_blocks = ["0.0.0.0/0"]
              }
            }
            """
        }
    )
    assert response.valid is False
    assert any(finding.code == "PUBLIC_DATABASE" for finding in response.findings)
