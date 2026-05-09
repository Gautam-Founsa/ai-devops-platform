from app.schemas.kubernetes import ManifestGenerateRequest
from app.services.kubernetes import KubernetesIntelligenceService


def test_kubernetes_overview_has_pod_counts() -> None:
    overview = KubernetesIntelligenceService().cluster_overview()
    assert overview.nodes_ready <= overview.nodes_total
    assert overview.pods_failed >= 1


def test_manifest_generation_includes_probes_and_resources() -> None:
    manifest = KubernetesIntelligenceService().generate_manifest(
        ManifestGenerateRequest(app_name="Inventory API", image="example.com/inventory:v1")
    )
    assert "kind: Deployment" in manifest.yaml
    assert "readinessProbe" in manifest.yaml
    assert "resources" in manifest.yaml

