from __future__ import annotations

import re
from typing import Any

import yaml

from app.schemas.kubernetes import (
    ClusterOverview,
    CrashLoopAnalysisResponse,
    ManifestGenerateRequest,
    ManifestGenerateResponse,
    PodSummary,
    ResourceRecommendation,
    YamlExplainResponse,
)


class KubernetesIntelligenceService:
    def cluster_overview(self) -> ClusterOverview:
        pods = self.pods()
        return ClusterOverview(
            name="production-us-east",
            provider="eks",
            region="us-east-1",
            status="degraded",
            nodes_ready=8,
            nodes_total=8,
            namespaces=7,
            pods_running=len([pod for pod in pods if pod.status == "Running"]),
            pods_pending=len([pod for pod in pods if pod.status == "Pending"]),
            pods_failed=len([pod for pod in pods if pod.status not in {"Running", "Pending"}]),
            cpu_request_percent=68.4,
            memory_request_percent=74.2,
        )

    def pods(self, namespace: str | None = None) -> list[PodSummary]:
        pods = [
            PodSummary(
                name="checkout-api-7f49c9d5b8-pq2md",
                namespace="payments",
                workload="checkout-api",
                status="CrashLoopBackOff",
                restarts=17,
                cpu_millicores=280,
                memory_mib=512,
                age="42m",
                node="ip-10-0-42-18",
                reason="Back-off restarting failed container",
            ),
            PodSummary(
                name="payment-worker-6d9967b8dd-2x8kf",
                namespace="payments",
                workload="payment-worker",
                status="Running",
                restarts=1,
                cpu_millicores=190,
                memory_mib=384,
                age="3h",
                node="ip-10-0-40-21",
            ),
            PodSummary(
                name="api-gateway-84dcbc9856-7v2pk",
                namespace="edge",
                workload="api-gateway",
                status="Running",
                restarts=0,
                cpu_millicores=340,
                memory_mib=256,
                age="8h",
                node="ip-10-0-41-12",
            ),
            PodSummary(
                name="metrics-ingester-6466c866df-vvx9l",
                namespace="observability",
                workload="metrics-ingester",
                status="Pending",
                restarts=0,
                cpu_millicores=0,
                memory_mib=0,
                age="19m",
                node="unscheduled",
                reason="Insufficient cpu",
            ),
        ]
        if namespace:
            return [pod for pod in pods if pod.namespace == namespace]
        return pods

    def analyze_crash_loop(self, namespace: str, pod_name: str) -> CrashLoopAnalysisResponse:
        pod = self._find_pod(namespace, pod_name)
        evidence = [
            f"{pod.restarts} restarts observed in {pod.age}",
            pod.reason or "Container is not reporting a Kubernetes waiting reason",
            "Recent log pattern: connection timeout to payment-service:443",
            "Readiness probe fails before dependency client finishes warmup",
        ]
        likely_causes = [
            "Application exits during startup when the payment dependency is unavailable.",
            "Readiness/liveness probes may be too aggressive for the current startup path.",
            "Memory limit should be checked if OOMKilled appears in real pod events.",
        ]
        remediation_steps = [
            "Inspect previous container logs with `kubectl logs --previous`.",
            "Check pod events and deployment rollout history for the first failing revision.",
            "Increase startupProbe coverage or relax livenessProbe initialDelaySeconds.",
            "Validate downstream service DNS, NetworkPolicy, and secret/config references.",
        ]
        return CrashLoopAnalysisResponse(
            pod=pod,
            likely_causes=likely_causes,
            evidence=evidence,
            remediation_steps=remediation_steps,
        )

    def recommendations(self) -> list[ResourceRecommendation]:
        return [
            ResourceRecommendation(
                target="checkout-api",
                namespace="payments",
                recommendation="Raise memory request and set an explicit memory limit.",
                current="256Mi request / no limit",
                suggested="512Mi request / 768Mi limit",
                confidence=0.82,
                rationale="Observed working set is near request during rollout and restart bursts.",
            ),
            ResourceRecommendation(
                target="metrics-ingester",
                namespace="observability",
                recommendation="Reduce CPU request or add node capacity.",
                current="1000m request",
                suggested="500m request after profiling, or add one general-purpose node",
                confidence=0.76,
                rationale="Pod is Pending because the scheduler reports insufficient CPU.",
            ),
            ResourceRecommendation(
                target="api-gateway",
                namespace="edge",
                recommendation="Add horizontal pod autoscaling on CPU and request rate.",
                current="2 static replicas",
                suggested="min 2 / max 8, target 65% CPU",
                confidence=0.71,
                rationale="Gateway CPU is steady but burst-prone at peak traffic windows.",
            ),
        ]

    def explain_yaml(self, raw_yaml: str) -> YamlExplainResponse:
        try:
            manifest = yaml.safe_load(raw_yaml)
        except yaml.YAMLError as exc:
            raise ValueError("Invalid Kubernetes YAML") from exc
        if not isinstance(manifest, dict):
            raise ValueError("YAML must contain a Kubernetes object")

        kind = str(manifest.get("kind", "Unknown"))
        metadata = manifest.get("metadata") or {}
        spec = manifest.get("spec") or {}
        name = str(metadata.get("name", "unnamed"))
        namespace = str(metadata.get("namespace", "default"))
        risks: list[str] = []
        recommendations: list[str] = []

        containers = self._containers(manifest)
        if containers and any("resources" not in container for container in containers):
            risks.append("One or more containers do not declare resource requests or limits.")
            recommendations.append("Set CPU and memory requests for scheduler stability.")
        if kind == "Deployment" and int(spec.get("replicas", 1)) < 2:
            risks.append("Deployment has fewer than two replicas.")
            recommendations.append("Use at least two replicas for production workloads.")
        if containers and any(not container.get("readinessProbe") for container in containers):
            recommendations.append("Add readiness probes so traffic only reaches ready pods.")
        if not risks:
            risks.append("No high-confidence structural risks found in this manifest.")

        return YamlExplainResponse(
            kind=kind,
            name=name,
            namespace=namespace,
            summary=f"{kind} `{name}` in namespace `{namespace}` declares {len(containers)} container(s).",
            risks=risks,
            recommendations=recommendations,
        )

    def generate_manifest(self, payload: ManifestGenerateRequest) -> ManifestGenerateResponse:
        safe_name = re.sub(r"[^a-z0-9-]+", "-", payload.app_name.lower()).strip("-")
        if not safe_name:
            safe_name = "generated-app"
        manifest: dict[str, Any] = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": safe_name, "namespace": payload.namespace},
            "spec": {
                "replicas": payload.replicas,
                "selector": {"matchLabels": {"app": safe_name}},
                "template": {
                    "metadata": {"labels": {"app": safe_name}},
                    "spec": {
                        "containers": [
                            {
                                "name": safe_name,
                                "image": payload.image,
                                "ports": [{"containerPort": payload.port}],
                                "resources": {
                                    "requests": {
                                        "cpu": payload.cpu_request,
                                        "memory": payload.memory_request,
                                    },
                                    "limits": {
                                        "cpu": self._double_cpu(payload.cpu_request),
                                        "memory": self._double_memory(payload.memory_request),
                                    },
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": "/health", "port": payload.port},
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 10,
                                },
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": payload.port},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 20,
                                },
                            }
                        ]
                    },
                },
            },
        }
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": safe_name, "namespace": payload.namespace},
            "spec": {
                "selector": {"app": safe_name},
                "ports": [{"port": payload.port, "targetPort": payload.port}],
            },
        }
        yaml_text = yaml.safe_dump_all([manifest, service], sort_keys=False)
        return ManifestGenerateResponse(
            yaml=yaml_text,
            notes=[
                "Generated Deployment and ClusterIP Service with probes and resource controls.",
                "Review image pull secrets, service account, NetworkPolicy, and HPA before production.",
            ],
        )

    def _find_pod(self, namespace: str, pod_name: str) -> PodSummary:
        for pod in self.pods(namespace):
            if pod.name == pod_name:
                return pod
        return PodSummary(
            name=pod_name,
            namespace=namespace,
            workload=pod_name.rsplit("-", 2)[0],
            status="CrashLoopBackOff",
            restarts=5,
            cpu_millicores=120,
            memory_mib=256,
            age="unknown",
            node="unknown",
            reason="Back-off restarting failed container",
        )

    def _containers(self, manifest: dict) -> list[dict]:
        if manifest.get("kind") == "Pod":
            return list((manifest.get("spec") or {}).get("containers") or [])
        return list(
            (((manifest.get("spec") or {}).get("template") or {}).get("spec") or {}).get(
                "containers"
            )
            or []
        )

    def _double_cpu(self, cpu: str) -> str:
        if cpu.endswith("m"):
            return f"{int(cpu[:-1]) * 2}m"
        return str(int(float(cpu) * 2))

    def _double_memory(self, memory: str) -> str:
        match = re.match(r"^(\d+)(Mi|Gi)$", memory)
        if not match:
            return memory
        value, unit = match.groups()
        return f"{int(value) * 2}{unit}"
