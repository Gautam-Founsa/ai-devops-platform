from __future__ import annotations

import re
import textwrap

from app.schemas.terraform import (
    TerraformGenerateRequest,
    TerraformGenerateResponse,
    TerraformTemplateResponse,
    TerraformValidationFinding,
    TerraformValidateResponse,
)


class TerraformGeneratorService:
    def templates(self) -> list[TerraformTemplateResponse]:
        return [
            TerraformTemplateResponse(
                id="ecs",
                name="AWS ECS Fargate",
                description="VPC-aware ECS service with task definition, logs, IAM, and autoscaling-ready defaults.",
                resources=[
                    "aws_ecs_cluster",
                    "aws_ecs_service",
                    "aws_ecs_task_definition",
                    "aws_cloudwatch_log_group",
                ],
            ),
            TerraformTemplateResponse(
                id="rds",
                name="AWS RDS PostgreSQL",
                description="Encrypted private PostgreSQL database with subnet group and least-open security group.",
                resources=["aws_db_instance", "aws_db_subnet_group", "aws_security_group"],
            ),
            TerraformTemplateResponse(
                id="alb",
                name="AWS Application Load Balancer",
                description="Public ALB, target group, listener, and health checks for HTTP workloads.",
                resources=["aws_lb", "aws_lb_target_group", "aws_lb_listener"],
            ),
            TerraformTemplateResponse(
                id="ecs-rds-alb",
                name="ECS + RDS + ALB",
                description="Production web service baseline combining ECS Fargate, RDS PostgreSQL, and ALB.",
                resources=[
                    "aws_ecs_cluster",
                    "aws_ecs_service",
                    "aws_db_instance",
                    "aws_lb",
                    "aws_security_group",
                ],
            ),
        ]

    def generate(self, payload: TerraformGenerateRequest) -> TerraformGenerateResponse:
        context = self._context(payload)
        files = {
            "versions.tf": self._versions_tf(),
            "variables.tf": self._variables_tf(context),
            "network.tf": self._network_tf(context),
            "security.tf": self._security_tf(context),
            "outputs.tf": self._outputs_tf(),
        }
        if payload.template in {"ecs", "ecs-rds-alb"}:
            files["ecs.tf"] = self._ecs_tf(context)
        if payload.template in {"rds", "ecs-rds-alb"}:
            files["rds.tf"] = self._rds_tf(context)
        if payload.template in {"alb", "ecs-rds-alb"}:
            files["alb.tf"] = self._alb_tf(context)

        validation = self.validate(files).findings
        return TerraformGenerateResponse(
            template=payload.template,
            files=files,
            explanation=self._explanation(payload),
            security_best_practices=self.security_best_practices(payload.template),
            validation=validation,
        )

    def validate(self, files: dict[str, str]) -> TerraformValidateResponse:
        hcl = "\n".join(files.values())
        findings: list[TerraformValidationFinding] = []

        if not re.search(r'required_version\s*=\s*">= 1\.6\.0"', hcl):
            findings.append(
                self._finding(
                    "medium",
                    "TF_VERSION_PIN",
                    "Terraform version is not pinned to a modern minimum.",
                    "Set required_version to >= 1.6.0 and pin provider major versions.",
                )
            )
        if "encrypt" not in hcl and "storage_encrypted" not in hcl:
            findings.append(
                self._finding(
                    "high",
                    "ENCRYPTION_MISSING",
                    "No encryption setting was detected.",
                    "Enable encryption for data stores, logs, and stateful resources.",
                )
            )
        if self._has_public_database_ingress(hcl):
            findings.append(
                self._finding(
                    "critical",
                    "PUBLIC_DATABASE",
                    "Database ingress appears open to the internet.",
                    "Restrict database ingress to the application security group.",
                )
            )
        if "skip_final_snapshot = true" in hcl:
            findings.append(
                self._finding(
                    "medium",
                    "RDS_FINAL_SNAPSHOT_DISABLED",
                    "RDS final snapshots are disabled.",
                    "Enable final snapshots for production databases.",
                )
            )
        if "aws_cloudwatch_log_group" in hcl and "retention_in_days" not in hcl:
            findings.append(
                self._finding(
                    "low",
                    "LOG_RETENTION_MISSING",
                    "CloudWatch log retention is not configured.",
                    "Set a retention period that matches compliance and cost requirements.",
                )
            )
        if "resource " not in hcl:
            findings.append(
                self._finding(
                    "high",
                    "NO_RESOURCES",
                    "No Terraform resources were found.",
                    "Generate or provide at least one Terraform resource block.",
                )
            )

        return TerraformValidateResponse(
            valid=not any(f.severity in {"critical", "high"} for f in findings),
            findings=findings,
        )

    def validate_hcl(self, hcl: str | None, files: dict[str, str]) -> TerraformValidateResponse:
        if hcl:
            files = {"main.tf": hcl}
        return self.validate(files)

    def _has_public_database_ingress(self, hcl: str) -> bool:
        ingress_blocks = re.findall(r"ingress\s*\{(?P<body>.*?)\n\s*\}", hcl, flags=re.DOTALL)
        return any(
            "from_port   = 5432" in block and 'cidr_blocks = ["0.0.0.0/0"]' in block
            for block in ingress_blocks
        )

    def security_best_practices(self, template: str) -> list[str]:
        practices = [
            "Keep Terraform state in an encrypted remote backend with locking.",
            "Pin provider versions and review plans before apply.",
            "Use least-privilege security groups and avoid public database ingress.",
            "Tag resources with environment, owner, and cost-center metadata.",
        ]
        if template in {"rds", "ecs-rds-alb"}:
            practices.extend(
                [
                    "Enable RDS storage encryption, backup retention, deletion protection, and final snapshots.",
                    "Store database credentials in Secrets Manager or SSM Parameter Store, not in Terraform variables.",
                ]
            )
        if template in {"ecs", "ecs-rds-alb"}:
            practices.extend(
                [
                    "Send container logs to CloudWatch with explicit retention.",
                    "Run ECS tasks in private subnets behind an ALB.",
                ]
            )
        return practices

    def _context(self, payload: TerraformGenerateRequest) -> dict[str, str]:
        name = re.sub(r"[^a-z0-9-]+", "-", payload.app_name.lower()).strip("-") or "app"
        prompt = payload.prompt.lower()
        return {
            "name": name,
            "region": payload.region,
            "environment": payload.environment,
            "image": payload.container_image,
            "db_instance_class": "db.t4g.medium" if "production" in prompt or "prod" in prompt else "db.t4g.micro",
            "desired_count": "3" if "high availability" in prompt or "production" in prompt else "2",
        }

    def _versions_tf(self) -> str:
        return textwrap.dedent(
            """
            terraform {
              required_version = ">= 1.6.0"

              required_providers {
                aws = {
                  source  = "hashicorp/aws"
                  version = "~> 5.0"
                }
              }
            }

            provider "aws" {
              region = var.region

              default_tags {
                tags = local.tags
              }
            }
            """
        ).strip()

    def _variables_tf(self, context: dict[str, str]) -> str:
        return textwrap.dedent(
            f"""
            variable "region" {{
              type    = string
              default = "{context["region"]}"
            }}

            variable "environment" {{
              type    = string
              default = "{context["environment"]}"
            }}

            variable "container_image" {{
              type    = string
              default = "{context["image"]}"
            }}

            locals {{
              name = "{context["name"]}"
              tags = {{
                Project     = local.name
                Environment = var.environment
                ManagedBy   = "terraform"
              }}
            }}
            """
        ).strip()

    def _network_tf(self, context: dict[str, str]) -> str:
        del context
        return textwrap.dedent(
            """
            data "aws_availability_zones" "available" {
              state = "available"
            }

            resource "aws_vpc" "main" {
              cidr_block           = "10.42.0.0/16"
              enable_dns_hostnames = true
              enable_dns_support   = true
            }

            resource "aws_subnet" "public" {
              count                   = 2
              vpc_id                  = aws_vpc.main.id
              cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
              availability_zone       = data.aws_availability_zones.available.names[count.index]
              map_public_ip_on_launch = true
            }

            resource "aws_subnet" "private" {
              count             = 2
              vpc_id            = aws_vpc.main.id
              cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
              availability_zone = data.aws_availability_zones.available.names[count.index]
            }
            """
        ).strip()

    def _security_tf(self, context: dict[str, str]) -> str:
        del context
        return textwrap.dedent(
            """
            resource "aws_security_group" "alb" {
              name        = "${local.name}-alb"
              description = "Allow HTTP ingress to the load balancer"
              vpc_id      = aws_vpc.main.id

              ingress {
                from_port   = 80
                to_port     = 80
                protocol    = "tcp"
                cidr_blocks = ["0.0.0.0/0"]
              }

              egress {
                from_port   = 0
                to_port     = 0
                protocol    = "-1"
                cidr_blocks = ["0.0.0.0/0"]
              }
            }

            resource "aws_security_group" "app" {
              name        = "${local.name}-app"
              description = "Allow ALB traffic to ECS tasks"
              vpc_id      = aws_vpc.main.id

              ingress {
                from_port       = 8080
                to_port         = 8080
                protocol        = "tcp"
                security_groups = [aws_security_group.alb.id]
              }

              egress {
                from_port   = 0
                to_port     = 0
                protocol    = "-1"
                cidr_blocks = ["0.0.0.0/0"]
              }
            }

            resource "aws_security_group" "database" {
              name        = "${local.name}-database"
              description = "Allow PostgreSQL from ECS tasks only"
              vpc_id      = aws_vpc.main.id

              ingress {
                from_port       = 5432
                to_port         = 5432
                protocol        = "tcp"
                security_groups = [aws_security_group.app.id]
              }
            }
            """
        ).strip()

    def _ecs_tf(self, context: dict[str, str]) -> str:
        return textwrap.dedent(
            f"""
            resource "aws_cloudwatch_log_group" "app" {{
              name              = "/ecs/${{local.name}}"
              retention_in_days = 30
            }}

            resource "aws_ecs_cluster" "main" {{
              name = local.name

              setting {{
                name  = "containerInsights"
                value = "enabled"
              }}
            }}

            resource "aws_iam_role" "task_execution" {{
              name = "${{local.name}}-task-execution"
              assume_role_policy = jsonencode({{
                Version = "2012-10-17"
                Statement = [{{
                  Action = "sts:AssumeRole"
                  Effect = "Allow"
                  Principal = {{ Service = "ecs-tasks.amazonaws.com" }}
                }}]
              }})
            }}

            resource "aws_iam_role_policy_attachment" "task_execution" {{
              role       = aws_iam_role.task_execution.name
              policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
            }}

            resource "aws_ecs_task_definition" "app" {{
              family                   = local.name
              network_mode             = "awsvpc"
              requires_compatibilities = ["FARGATE"]
              cpu                      = 512
              memory                   = 1024
              execution_role_arn       = aws_iam_role.task_execution.arn

              container_definitions = jsonencode([{{
                name      = local.name
                image     = var.container_image
                essential = true
                portMappings = [{{ containerPort = 8080, protocol = "tcp" }}]
                logConfiguration = {{
                  logDriver = "awslogs"
                  options = {{
                    awslogs-group         = aws_cloudwatch_log_group.app.name
                    awslogs-region        = var.region
                    awslogs-stream-prefix = "app"
                  }}
                }}
              }}])
            }}

            resource "aws_ecs_service" "app" {{
              name            = local.name
              cluster         = aws_ecs_cluster.main.id
              task_definition = aws_ecs_task_definition.app.arn
              desired_count   = {context["desired_count"]}
              launch_type     = "FARGATE"

              network_configuration {{
                subnets          = aws_subnet.private[*].id
                security_groups  = [aws_security_group.app.id]
                assign_public_ip = false
              }}

              load_balancer {{
                target_group_arn = aws_lb_target_group.app.arn
                container_name   = local.name
                container_port   = 8080
              }}
            }}
            """
        ).strip()

    def _rds_tf(self, context: dict[str, str]) -> str:
        return textwrap.dedent(
            f"""
            resource "aws_db_subnet_group" "main" {{
              name       = local.name
              subnet_ids = aws_subnet.private[*].id
            }}

            resource "aws_db_instance" "postgres" {{
              identifier                  = "${{local.name}}-postgres"
              engine                      = "postgres"
              engine_version              = "16"
              instance_class              = "{context["db_instance_class"]}"
              allocated_storage           = 50
              max_allocated_storage       = 200
              db_subnet_group_name        = aws_db_subnet_group.main.name
              vpc_security_group_ids      = [aws_security_group.database.id]
              storage_encrypted           = true
              backup_retention_period     = 7
              deletion_protection         = true
              skip_final_snapshot         = false
              final_snapshot_identifier   = "${{local.name}}-final-snapshot"
              manage_master_user_password = true
              publicly_accessible         = false
            }}
            """
        ).strip()

    def _alb_tf(self, context: dict[str, str]) -> str:
        del context
        return textwrap.dedent(
            """
            resource "aws_lb" "app" {
              name               = local.name
              load_balancer_type = "application"
              internal           = false
              security_groups    = [aws_security_group.alb.id]
              subnets            = aws_subnet.public[*].id
            }

            resource "aws_lb_target_group" "app" {
              name        = local.name
              port        = 8080
              protocol    = "HTTP"
              target_type = "ip"
              vpc_id      = aws_vpc.main.id

              health_check {
                path                = "/health"
                matcher             = "200-399"
                healthy_threshold   = 2
                unhealthy_threshold = 3
              }
            }

            resource "aws_lb_listener" "http" {
              load_balancer_arn = aws_lb.app.arn
              port              = 80
              protocol          = "HTTP"

              default_action {
                type             = "forward"
                target_group_arn = aws_lb_target_group.app.arn
              }
            }
            """
        ).strip()

    def _outputs_tf(self) -> str:
        return textwrap.dedent(
            """
            output "alb_dns_name" {
              value       = try(aws_lb.app.dns_name, null)
              description = "Application load balancer DNS name"
            }

            output "database_endpoint" {
              value       = try(aws_db_instance.postgres.address, null)
              description = "Private RDS endpoint"
              sensitive   = true
            }
            """
        ).strip()

    def _explanation(self, payload: TerraformGenerateRequest) -> str:
        return (
            f"Generated `{payload.template}` Terraform for `{payload.app_name}` in `{payload.region}`. "
            "The design favors private application/data tiers, encrypted storage, pinned providers, "
            "CloudWatch logging, and least-privilege network paths."
        )

    def _finding(
        self,
        severity: str,
        code: str,
        message: str,
        recommendation: str,
    ) -> TerraformValidationFinding:
        return TerraformValidationFinding(
            severity=severity,
            code=code,
            message=message,
            recommendation=recommendation,
        )
