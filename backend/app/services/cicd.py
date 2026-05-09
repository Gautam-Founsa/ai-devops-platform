from __future__ import annotations

from copy import deepcopy
from typing import Any

import yaml

from app.schemas.cicd import (
    CicdAnalyzeResponse,
    CicdFinding,
    CicdOptimizeResponse,
    WorkflowJobSummary,
)


class CicdAnalyzerService:
    def analyze(self, workflow_yaml: str, repository: str | None = None) -> CicdAnalyzeResponse:
        del repository
        workflow = self._load(workflow_yaml)
        jobs = workflow.get("jobs") or {}
        if not isinstance(jobs, dict):
            jobs = {}

        summaries = [
            self._job_summary(name, job)
            for name, job in jobs.items()
            if isinstance(job, dict)
        ]
        findings = self._findings(workflow, summaries)
        caching = self._caching_suggestions(workflow, summaries)
        parallel = self._parallelization_suggestions(workflow, summaries)
        security = self.security_best_practices(workflow, summaries)
        score = max(0, 100 - sum(self._penalty(finding.severity) for finding in findings))

        triggers = workflow.get("on", [])
        if isinstance(triggers, dict):
            trigger_names = [str(key) for key in triggers.keys()]
        elif isinstance(triggers, list):
            trigger_names = [str(item) for item in triggers]
        else:
            trigger_names = [str(triggers)]

        return CicdAnalyzeResponse(
            workflow_name=str(workflow.get("name", "GitHub Actions workflow")),
            triggers=trigger_names,
            jobs=summaries,
            findings=findings,
            caching_suggestions=caching,
            parallelization_suggestions=parallel,
            security_best_practices=security,
            score=score,
        )

    def optimize(self, workflow_yaml: str, goals: list[str]) -> CicdOptimizeResponse:
        workflow = self._load(workflow_yaml)
        optimized = deepcopy(workflow)
        changes: list[str] = []

        optimized.setdefault("permissions", {"contents": "read"})
        if "permissions" not in workflow:
            changes.append("Added top-level read-only GitHub token permissions.")

        jobs = optimized.setdefault("jobs", {})
        if isinstance(jobs, dict):
            for job_name, job in jobs.items():
                if not isinstance(job, dict):
                    continue
                steps = job.setdefault("steps", [])
                if not isinstance(steps, list):
                    continue
                if not job.get("timeout-minutes"):
                    job["timeout-minutes"] = 20
                    changes.append(f"Added timeout-minutes to `{job_name}`.")
                if self._looks_like_node_job(steps) and not self._has_cache(steps):
                    steps.insert(
                        self._insert_after_checkout(steps),
                        {
                            "name": "Cache npm dependencies",
                            "uses": "actions/cache@v4",
                            "with": {
                                "path": "~/.npm",
                                "key": "${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}",
                                "restore-keys": "${{ runner.os }}-npm-",
                            },
                        },
                    )
                    changes.append(f"Added npm dependency caching to `{job_name}`.")
                if self._looks_like_python_job(steps) and not self._has_cache(steps):
                    steps.insert(
                        self._insert_after_checkout(steps),
                        {
                            "name": "Cache pip dependencies",
                            "uses": "actions/cache@v4",
                            "with": {
                                "path": "~/.cache/pip",
                                "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}",
                                "restore-keys": "${{ runner.os }}-pip-",
                            },
                        },
                    )
                    changes.append(f"Added pip dependency caching to `{job_name}`.")
                if "parallel" in goals and not job.get("strategy") and "test" in job_name.lower():
                    job["strategy"] = {"fail-fast": False, "matrix": {"shard": [1, 2]}}
                    changes.append(f"Added a test shard matrix to `{job_name}`.")

        optimized_yaml = yaml.safe_dump(optimized, sort_keys=False)
        return CicdOptimizeResponse(
            optimized_workflow_yaml=optimized_yaml,
            changes=changes or ["Workflow already follows the Phase 5 optimization baseline."],
            analysis=self.analyze(optimized_yaml),
        )

    def security_best_practices(
        self,
        workflow: dict[str, Any],
        summaries: list[WorkflowJobSummary],
    ) -> list[str]:
        practices = [
            "Use least-privilege `permissions` at the workflow or job level.",
            "Pin third-party actions to immutable SHAs for production release workflows.",
            "Avoid echoing secrets and pass credentials through GitHub secrets or OIDC.",
            "Use environment protection rules for deployments.",
        ]
        if any(not summary.has_timeout for summary in summaries):
            practices.append("Set `timeout-minutes` on every job to limit hung runner cost and blast radius.")
        if "pull_request_target" in self._trigger_names(workflow):
            practices.append("Avoid checking out untrusted pull request code with elevated `pull_request_target` permissions.")
        return practices

    def _load(self, workflow_yaml: str) -> dict[str, Any]:
        try:
            loaded = yaml.safe_load(workflow_yaml)
        except yaml.YAMLError as exc:
            raise ValueError("Invalid GitHub Actions YAML") from exc
        if not isinstance(loaded, dict):
            raise ValueError("Workflow YAML must be a mapping")
        if True in loaded and "on" not in loaded:
            loaded["on"] = loaded.pop(True)
        return loaded

    def _job_summary(self, name: str, job: dict[str, Any]) -> WorkflowJobSummary:
        steps = job.get("steps") if isinstance(job.get("steps"), list) else []
        return WorkflowJobSummary(
            name=name,
            runs_on=str(job.get("runs-on", "unspecified")),
            steps=len(steps),
            uses_cache=self._has_cache(steps),
            uploads_artifacts=any("upload-artifact" in str(step.get("uses", "")) for step in steps if isinstance(step, dict)),
            has_permissions="permissions" in job,
            has_timeout="timeout-minutes" in job,
            matrix=bool((job.get("strategy") or {}).get("matrix")) if isinstance(job.get("strategy"), dict) else False,
        )

    def _findings(self, workflow: dict[str, Any], summaries: list[WorkflowJobSummary]) -> list[CicdFinding]:
        findings: list[CicdFinding] = []
        if "permissions" not in workflow and any(not summary.has_permissions for summary in summaries):
            findings.append(
                self._finding(
                    "high",
                    "security",
                    "GitHub token permissions are not constrained.",
                    "Default token permissions may be broader than required.",
                    "Add top-level `permissions: contents: read` and grant write scopes only to deploy jobs.",
                )
            )
        for summary in summaries:
            if not summary.has_timeout:
                findings.append(
                    self._finding(
                        "medium",
                        "reliability",
                        f"`{summary.name}` has no timeout.",
                        "Hung jobs can consume runner minutes and block deployment feedback.",
                        "Set `timeout-minutes` based on normal job duration plus a small buffer.",
                    )
                )
            if self._job_likely_installs_dependencies(summary.name) and not summary.uses_cache:
                findings.append(
                    self._finding(
                        "medium",
                        "performance",
                        f"`{summary.name}` does not use dependency caching.",
                        "Repeated package installation slows feedback loops.",
                        "Use `actions/cache@v4` or setup-* built-in caching for npm, pip, pnpm, Maven, or Gradle.",
                    )
                )
            if "test" in summary.name.lower() and not summary.matrix and summary.steps >= 5:
                findings.append(
                    self._finding(
                        "low",
                        "parallelization",
                        f"`{summary.name}` may benefit from matrix parallelization.",
                        "Large test jobs often serialize independent work.",
                        "Split tests by language, package, shard, or runtime matrix.",
                    )
                )
        if "pull_request_target" in self._trigger_names(workflow):
            findings.append(
                self._finding(
                    "critical",
                    "security",
                    "`pull_request_target` trigger detected.",
                    "This trigger can expose elevated token permissions to untrusted PR workflows.",
                    "Use `pull_request` for CI and reserve `pull_request_target` for carefully reviewed label/comment automation.",
                )
            )
        return findings

    def _caching_suggestions(
        self,
        workflow: dict[str, Any],
        summaries: list[WorkflowJobSummary],
    ) -> list[str]:
        del workflow
        suggestions = []
        if any(not summary.uses_cache for summary in summaries):
            suggestions.append("Cache package-manager directories keyed by lockfiles to avoid repeated dependency downloads.")
            suggestions.append("Prefer setup-node/setup-python built-in cache options when they match the package manager.")
        if any(summary.uploads_artifacts for summary in summaries):
            suggestions.append("Set artifact retention days explicitly to control storage cost.")
        return suggestions or ["Caching baseline looks healthy."]

    def _parallelization_suggestions(
        self,
        workflow: dict[str, Any],
        summaries: list[WorkflowJobSummary],
    ) -> list[str]:
        del workflow
        suggestions = []
        if len(summaries) == 1:
            suggestions.append("Split lint, typecheck, unit tests, and build into separate jobs for faster feedback.")
        if any("test" in summary.name.lower() and not summary.matrix for summary in summaries):
            suggestions.append("Use a matrix strategy to shard test suites or run language versions in parallel.")
        if any(summary.matrix for summary in summaries):
            suggestions.append("Use `fail-fast: false` for matrix tests when you want complete failure visibility.")
        return suggestions or ["Parallelization baseline looks healthy."]

    def _trigger_names(self, workflow: dict[str, Any]) -> list[str]:
        triggers = workflow.get("on", [])
        if isinstance(triggers, dict):
            return [str(key) for key in triggers.keys()]
        if isinstance(triggers, list):
            return [str(trigger) for trigger in triggers]
        return [str(triggers)]

    def _has_cache(self, steps: list[Any]) -> bool:
        for step in steps:
            if not isinstance(step, dict):
                continue
            if "actions/cache" in str(step.get("uses", "")):
                return True
            with_block = step.get("with")
            if isinstance(with_block, dict) and "cache" in with_block:
                return True
        return False

    def _looks_like_node_job(self, steps: list[Any]) -> bool:
        dumped = yaml.safe_dump(steps).lower()
        return "setup-node" in dumped or "npm " in dumped or "pnpm " in dumped or "yarn " in dumped

    def _looks_like_python_job(self, steps: list[Any]) -> bool:
        dumped = yaml.safe_dump(steps).lower()
        return "setup-python" in dumped or "pip install" in dumped or "pytest" in dumped

    def _insert_after_checkout(self, steps: list[Any]) -> int:
        for index, step in enumerate(steps):
            if isinstance(step, dict) and "actions/checkout" in str(step.get("uses", "")):
                return index + 1
        return 0

    def _job_likely_installs_dependencies(self, job_name: str) -> bool:
        lowered = job_name.lower()
        return any(term in lowered for term in ["build", "test", "lint", "type", "ci"])

    def _penalty(self, severity: str) -> int:
        return {"critical": 30, "high": 20, "medium": 10, "low": 5}.get(severity, 5)

    def _finding(
        self,
        severity: str,
        category: str,
        title: str,
        detail: str,
        recommendation: str,
    ) -> CicdFinding:
        return CicdFinding(
            severity=severity,
            category=category,
            title=title,
            detail=detail,
            recommendation=recommendation,
        )
