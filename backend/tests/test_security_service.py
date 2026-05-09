from app.schemas.security import SecurityScanFile
from app.services.security import SecurityScannerService


def test_detects_secret_and_misconfiguration_without_db() -> None:
    service = SecurityScannerService(db=None)  # type: ignore[arg-type]
    file = SecurityScanFile(
        path="deploy.yaml",
        content='image: nginx:latest\nenv:\n  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"\n',
    )
    secrets = service._detect_secrets(file)
    misconfigs = service._detect_misconfigurations(file)
    assert secrets
    assert any(finding.title == "Mutable latest image tag detected" for finding in misconfigs)


def test_cve_enrichment_matches_known_package() -> None:
    service = SecurityScannerService(db=None)  # type: ignore[arg-type]
    findings = service._enrich_cves(SecurityScanFile(path="package.txt", content="log4j-core 2.14.1"))
    assert findings[0].cve_id == "CVE-2021-44228"

