from app.services.cicd import CicdAnalyzerService


SAMPLE = """
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npm test
      - run: npm run build
"""


def test_analyze_detects_missing_cache_and_permissions() -> None:
    response = CicdAnalyzerService().analyze(SAMPLE)
    codes = {finding.category for finding in response.findings}
    assert "performance" in codes
    assert "security" in codes
    assert response.score < 100


def test_optimize_adds_cache_and_timeout() -> None:
    response = CicdAnalyzerService().optimize(SAMPLE, goals=["parallel"])
    assert "actions/cache@v4" in response.optimized_workflow_yaml
    assert "timeout-minutes" in response.optimized_workflow_yaml

