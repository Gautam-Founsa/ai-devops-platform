from app.schemas.cost import (
    CostBreakdownItem,
    CostRecommendationResponse,
    CostSummaryResponse,
    CostTrendPoint,
)


class CostOptimizationService:
    def summary(self) -> CostSummaryResponse:
        recommendations = self.recommendations()
        rightsizing = sum(
            item.estimated_monthly_savings
            for item in recommendations
            if item.category == "rightsizing"
        )
        idle = sum(
            item.estimated_monthly_savings
            for item in recommendations
            if item.category == "idle-resource"
        )
        return CostSummaryResponse(
            currency="USD",
            month_to_date=14382.64,
            forecast_monthly=21890.12,
            previous_month=20441.27,
            potential_savings=round(sum(item.estimated_monthly_savings for item in recommendations), 2),
            idle_spend=round(idle, 2),
            rightsizing_savings=round(rightsizing, 2),
            breakdown=[
                CostBreakdownItem(
                    service="EKS workloads",
                    category="compute",
                    monthly_cost=6840.35,
                    change_percent=8.4,
                    owner="platform",
                ),
                CostBreakdownItem(
                    service="RDS PostgreSQL",
                    category="database",
                    monthly_cost=4120.14,
                    change_percent=3.1,
                    owner="payments",
                ),
                CostBreakdownItem(
                    service="CloudWatch and Loki",
                    category="observability",
                    monthly_cost=2318.72,
                    change_percent=12.6,
                    owner="sre",
                ),
                CostBreakdownItem(
                    service="ALB and NAT",
                    category="network",
                    monthly_cost=1864.93,
                    change_percent=-1.8,
                    owner="edge",
                ),
                CostBreakdownItem(
                    service="EBS snapshots",
                    category="storage",
                    monthly_cost=746.18,
                    change_percent=18.2,
                    owner="shared",
                ),
            ],
            trend=[
                CostTrendPoint(date="May 01", amount=653.14),
                CostTrendPoint(date="May 05", amount=684.80),
                CostTrendPoint(date="May 09", amount=701.22),
                CostTrendPoint(date="May 13", amount=729.55),
                CostTrendPoint(date="May 17", amount=735.18),
                CostTrendPoint(date="May 21", amount=748.46),
            ],
        )

    def recommendations(self) -> list[CostRecommendationResponse]:
        return [
            CostRecommendationResponse(
                id="eks-checkout-rightsize",
                category="rightsizing",
                priority="high",
                resource="payments/checkout-api",
                service="EKS workloads",
                current_monthly_cost=1260.40,
                estimated_monthly_savings=378.12,
                title="Right-size checkout-api CPU requests",
                rationale="P95 CPU usage stays below 42% of requested cores during peak traffic.",
                action="Reduce CPU requests from 750m to 400m, then watch latency and HPA behavior for one deploy window.",
                confidence=0.86,
            ),
            CostRecommendationResponse(
                id="rds-reporting-idle",
                category="idle-resource",
                priority="critical",
                resource="reporting-postgres-dev",
                service="RDS PostgreSQL",
                current_monthly_cost=492.78,
                estimated_monthly_savings=492.78,
                title="Stop idle development RDS instance",
                rationale="Connection count and write IOPS remain near zero outside weekly smoke tests.",
                action="Snapshot the instance and schedule it only for test windows or migrate to a shared dev database.",
                confidence=0.94,
            ),
            CostRecommendationResponse(
                id="ebs-snapshot-retention",
                category="idle-resource",
                priority="medium",
                resource="orphaned-ebs-snapshots",
                service="EBS snapshots",
                current_monthly_cost=184.22,
                estimated_monthly_savings=121.60,
                title="Prune orphaned snapshot retention",
                rationale="Snapshots older than the retention policy have no attached AMI or active restore plan.",
                action="Apply lifecycle retention tags and delete snapshots beyond approved backup windows.",
                confidence=0.79,
            ),
            CostRecommendationResponse(
                id="logs-retention-rightsize",
                category="rightsizing",
                priority="medium",
                resource="application-log-retention",
                service="CloudWatch and Loki",
                current_monthly_cost=865.31,
                estimated_monthly_savings=246.18,
                title="Tier verbose logs after incident window",
                rationale="Debug and access logs account for growing hot storage volume after the seven-day investigation window.",
                action="Keep high-signal logs hot for seven days and route lower-value streams to cheaper retention tiers.",
                confidence=0.81,
            ),
            CostRecommendationResponse(
                id="nat-egress-idle",
                category="idle-resource",
                priority="low",
                resource="staging-nat-egress",
                service="ALB and NAT",
                current_monthly_cost=228.45,
                estimated_monthly_savings=96.40,
                title="Reduce idle staging NAT traffic",
                rationale="Nightly artifact pulls cross NAT even when staging workloads are scaled to zero.",
                action="Use VPC endpoints and schedule staging-only egress paths with environment uptime.",
                confidence=0.72,
            ),
        ]

