from app.services.cost import CostOptimizationService


def test_summary_matches_recommendation_savings() -> None:
    service = CostOptimizationService()
    recommendations = service.recommendations()
    summary = service.summary()
    assert summary.potential_savings == round(
        sum(item.estimated_monthly_savings for item in recommendations),
        2,
    )


def test_recommendations_include_rightsizing_and_idle_resources() -> None:
    categories = {item.category for item in CostOptimizationService().recommendations()}
    assert categories == {"rightsizing", "idle-resource"}

