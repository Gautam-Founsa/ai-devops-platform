from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import SecurityFinding
from app.schemas.security import (
    SecurityFindingResponse,
    SecurityScanFile,
    SecurityScanResponse,
    SecurityToolStatus,
)


class SecurityScannerService:
    SECRET_PATTERNS = [
        ("AWS_ACCESS_KEY_ID", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("AWS_SECRET_ACCESS_KEY", re.compile(r"(?i)aws(.{0,20})?(secret|private).{0,20}[=:]\s*['\"]?[A-Za-z0-9/+=]{32,}")),
        ("GENERIC_API_KEY", re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"][^'\"\n]{12,}['\"]")),
        ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ]

    VULN_DB = {
        "openssl": ("CVE-2023-0286", "3.0.8", "high", "Upgrade OpenSSL to a patched release."),
        "log4j-core": ("CVE-2021-44228", "2.17.1", "critical", "Upgrade Log4j and remove vulnerable transitive versions."),
        "django": ("CVE-2023-36053", "4.2.3", "medium", "Upgrade Django to the latest supported patch release."),
        "express": ("CVE-2022-24999", "4.18.2", "medium", "Upgrade Express and review body parser limits."),
    }

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def scan(
        self,
        organization_id: UUID,
        repository: str | None,
        files: list[SecurityScanFile],
        include_trivy: bool,
        include_semgrep: bool,
    ) -> SecurityScanResponse:
        if not files:
            files = self._demo_files()

        findings: list[SecurityFindingResponse] = []
        for file in files:
            findings.extend(self._detect_secrets(file))
            findings.extend(self._detect_misconfigurations(file))
            findings.extend(self._enrich_cves(file))

        tool_status = [
            self._tool_status("trivy", include_trivy),
            self._tool_status("semgrep", include_semgrep),
        ]
        if include_trivy:
            findings.extend(self._run_trivy_if_available(files))
        if include_semgrep:
            findings.extend(self._run_semgrep_if_available(files))

        persisted = []
        for finding in findings:
            model = SecurityFinding(
                organization_id=organization_id,
                scanner=finding.scanner,
                category=finding.category,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                file_path=finding.file_path,
                line=finding.line,
                cve_id=finding.cve_id,
                package_name=finding.package_name,
                installed_version=finding.installed_version,
                fixed_version=finding.fixed_version,
                recommendation=finding.recommendation,
                status=finding.status,
                metadata_json=finding.metadata,
            )
            self.db.add(model)
            persisted.append((finding, model))
        await self.db.commit()

        response_findings = []
        for finding, model in persisted:
            await self.db.refresh(model)
            response_findings.append(self._from_model(model))

        return SecurityScanResponse(
            repository=repository,
            summary=self._summary(response_findings),
            findings=response_findings,
            recommendations=self._recommendations(response_findings),
            tools=tool_status,
        )

    async def findings(self, organization_id: UUID) -> list[SecurityFindingResponse]:
        result = await self.db.execute(
            select(SecurityFinding)
            .where(SecurityFinding.organization_id == organization_id)
            .order_by(SecurityFinding.created_at.desc())
            .limit(100)
        )
        return [self._from_model(finding) for finding in result.scalars().all()]

    def _detect_secrets(self, file: SecurityScanFile) -> list[SecurityFindingResponse]:
        findings = []
        for line_number, line in enumerate(file.content.splitlines(), start=1):
            for name, pattern in self.SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        SecurityFindingResponse(
                            scanner="secrets",
                            category="secret",
                            severity="critical",
                            title=f"Potential {name} secret detected",
                            description="A credential-like value appears in source content.",
                            file_path=file.path,
                            line=line_number,
                            recommendation="Revoke the credential, remove it from history, and load it from a secrets manager.",
                            metadata={"pattern": name},
                        )
                    )
        return findings

    def _detect_misconfigurations(self, file: SecurityScanFile) -> list[SecurityFindingResponse]:
        text = file.content
        findings: list[SecurityFindingResponse] = []
        if "privileged: true" in text:
            findings.append(self._misconfig(file, "Privileged container enabled", "high", "Avoid privileged containers and grant only required Linux capabilities."))
        if "runAsUser: 0" in text or "USER root" in text:
            findings.append(self._misconfig(file, "Container runs as root", "high", "Run containers as a non-root user and set a pod/container securityContext."))
        if 'cidr_blocks = ["0.0.0.0/0"]' in text and "5432" in text:
            findings.append(self._misconfig(file, "Database port exposed publicly", "critical", "Restrict database ingress to application security groups or private CIDRs."))
        if "latest" in text and ("image:" in text or "FROM " in text):
            findings.append(self._misconfig(file, "Mutable latest image tag detected", "medium", "Pin images to immutable tags or digests."))
        if "skip_final_snapshot = true" in text:
            findings.append(self._misconfig(file, "RDS final snapshot disabled", "medium", "Enable final snapshots for production databases."))
        if "pull_request_target" in text:
            findings.append(self._misconfig(file, "Risky pull_request_target workflow trigger", "high", "Use pull_request for CI and reserve pull_request_target for tightly scoped automation."))
        return findings

    def _enrich_cves(self, file: SecurityScanFile) -> list[SecurityFindingResponse]:
        findings: list[SecurityFindingResponse] = []
        lowered = file.content.lower()
        for package, (cve, fixed, severity, recommendation) in self.VULN_DB.items():
            if package in lowered:
                version = self._extract_version(file.content, package)
                findings.append(
                    SecurityFindingResponse(
                        scanner="cve-enrichment",
                        category="vulnerability",
                        severity=severity,
                        title=f"{package} matches known vulnerable package intelligence",
                        description=f"{package} is associated with {cve} in the local enrichment catalog.",
                        file_path=file.path,
                        cve_id=cve,
                        package_name=package,
                        installed_version=version,
                        fixed_version=fixed,
                        recommendation=recommendation,
                        metadata={"source": "local-cve-catalog"},
                    )
                )
        return findings

    def _run_trivy_if_available(self, files: list[SecurityScanFile]) -> list[SecurityFindingResponse]:
        if shutil.which("trivy") is None:
            return []
        return self._run_external_json_scanner("trivy", ["trivy", "fs", "--format", "json", "."], files)

    def _run_semgrep_if_available(self, files: list[SecurityScanFile]) -> list[SecurityFindingResponse]:
        if shutil.which("semgrep") is None:
            return []
        return self._run_external_json_scanner("semgrep", ["semgrep", "--config", "auto", "--json", "."], files)

    def _run_external_json_scanner(
        self,
        name: str,
        command: list[str],
        files: list[SecurityScanFile],
    ) -> list[SecurityFindingResponse]:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                for file in files:
                    path = root / file.path
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(file.content)
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30, check=False)
                if not result.stdout:
                    return []
                return self._parse_external_json(name, result.stdout)
        except Exception:
            return []

    def _parse_external_json(self, name: str, payload: str) -> list[SecurityFindingResponse]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if name == "semgrep":
            return [
                SecurityFindingResponse(
                    scanner="semgrep",
                    category="static-analysis",
                    severity=str(result.get("extra", {}).get("severity", "medium")).lower(),
                    title=str(result.get("check_id", "Semgrep finding")),
                    description=str(result.get("extra", {}).get("message", "Semgrep detected a code security issue.")),
                    file_path=result.get("path"),
                    line=result.get("start", {}).get("line"),
                    recommendation="Review the Semgrep rule guidance and patch the affected code path.",
                    metadata={"raw": result.get("extra", {})},
                )
                for result in data.get("results", [])
            ]
        findings = []
        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []) or []:
                findings.append(
                    SecurityFindingResponse(
                        scanner="trivy",
                        category="vulnerability",
                        severity=str(vuln.get("Severity", "medium")).lower(),
                        title=str(vuln.get("Title") or vuln.get("VulnerabilityID", "Trivy vulnerability")),
                        description=str(vuln.get("Description", "Trivy detected a vulnerable dependency.")),
                        file_path=result.get("Target"),
                        cve_id=vuln.get("VulnerabilityID"),
                        package_name=vuln.get("PkgName"),
                        installed_version=vuln.get("InstalledVersion"),
                        fixed_version=vuln.get("FixedVersion"),
                        recommendation="Upgrade to the fixed version and rebuild the affected artifact.",
                        metadata={"primary_url": vuln.get("PrimaryURL")},
                    )
                )
        return findings

    def _tool_status(self, name: str, enabled: bool) -> SecurityToolStatus:
        available = shutil.which(name) is not None
        return SecurityToolStatus(
            name=name,
            enabled=enabled,
            integrated=True,
            mode="external-binary" if enabled and available else "static-fallback",
            detail=(
                f"{name} binary detected and will run during scans."
                if enabled and available
                else f"{name} integration is wired; install the binary in the backend image to enable native scans."
            ),
        )

    def _misconfig(
        self,
        file: SecurityScanFile,
        title: str,
        severity: str,
        recommendation: str,
    ) -> SecurityFindingResponse:
        return SecurityFindingResponse(
            scanner="misconfiguration",
            category="misconfiguration",
            severity=severity,
            title=title,
            description="Static configuration analysis found a risky infrastructure or pipeline setting.",
            file_path=file.path,
            recommendation=recommendation,
        )

    def _summary(self, findings: list[SecurityFindingResponse]) -> dict[str, int]:
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            summary[finding.severity] = summary.get(finding.severity, 0) + 1
        summary["total"] = len(findings)
        return summary

    def _recommendations(self, findings: list[SecurityFindingResponse]) -> list[str]:
        recs = [
            "Fail CI on critical secrets, public database exposure, and exploitable critical CVEs.",
            "Run Trivy for image, filesystem, IaC, and dependency scanning in CI.",
            "Run Semgrep with organization-approved rule packs for code security checks.",
        ]
        categories = {finding.category for finding in findings}
        if "secret" in categories:
            recs.append("Rotate exposed secrets immediately and add pre-commit secret scanning.")
        if "misconfiguration" in categories:
            recs.append("Codify secure defaults in reusable Terraform/Kubernetes modules.")
        if "vulnerability" in categories:
            recs.append("Prioritize upgrades with known fixed versions and rebuild downstream images.")
        return recs

    def _from_model(self, finding: SecurityFinding) -> SecurityFindingResponse:
        return SecurityFindingResponse(
            id=finding.id,
            scanner=finding.scanner,
            category=finding.category,
            severity=finding.severity,
            title=finding.title,
            description=finding.description,
            file_path=finding.file_path,
            line=finding.line,
            cve_id=finding.cve_id,
            package_name=finding.package_name,
            installed_version=finding.installed_version,
            fixed_version=finding.fixed_version,
            recommendation=finding.recommendation,
            status=finding.status,
            metadata=finding.metadata_json,
            created_at=finding.created_at,
        )

    def _extract_version(self, content: str, package: str) -> str | None:
        match = re.search(rf"{re.escape(package)}[=:@~^<>\s]+([0-9][A-Za-z0-9.\-+]*)", content, re.IGNORECASE)
        return match.group(1) if match else None

    def _demo_files(self) -> list[SecurityScanFile]:
        return [
            SecurityScanFile(
                path="Dockerfile",
                content="FROM node:latest\nUSER root\nRUN npm install express@4.16.0\n",
            ),
            SecurityScanFile(
                path="terraform/db.tf",
                content='resource "aws_security_group" "db" { ingress { from_port = 5432 cidr_blocks = ["0.0.0.0/0"] } }\n',
            ),
            SecurityScanFile(
                path=".env.example",
                content='AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"\n',
            ),
        ]

