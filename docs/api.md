# API

Base URL: `/api/v1`

Phase 1 also exposes compatibility routes at `/api` for the endpoint shape in the product brief.

## Auth

- `POST /auth/register`
- `POST /auth/login`

Both return a bearer token and user profile.

## Chat

- `POST /chat`

Requires `Authorization: Bearer <token>`.

```json
{
  "message": "Why is checkout latency high?"
}
```

## Metrics

- `GET /metrics/query?query=rate(http_requests_total[5m])`

Requires `Authorization: Bearer <token>`.

Prometheus scrape endpoint is exposed separately at `/metrics`.

## Logs

- `POST /logs/ingest`
- `POST /logs/search`

Log search uses ChromaDB when available and falls back to PostgreSQL keyword search during startup or local outages.

## Incidents

- `GET /incidents`
- `POST /incidents/analyze`

Incident analysis searches relevant logs, creates an incident, reconstructs a timeline, and returns recommended actions.

## Kubernetes

- `GET /k8s/overview`
- `GET /k8s/pods`
- `POST /k8s/crashloop/analyze`
- `GET /k8s/recommendations`
- `POST /k8s/explain`
- `POST /k8s/generate`

Phase 3 runs in demo intelligence mode and preserves the API boundary for a real cluster adapter.

## Terraform

- `GET /terraform/templates`
- `POST /terraform/generate`
- `POST /terraform/validate`

Phase 4 generates AWS ECS, RDS, and ALB Terraform from natural language intent and applies static security validation.

## CI/CD

- `POST /cicd/analyze`
- `POST /cicd/optimize`

Phase 5 parses GitHub Actions workflows, detects inefficiencies, suggests caching and parallelization, and recommends CI/CD security controls.

## Security

- `POST /security/scan`
- `GET /security/findings`

Phase 6 detects secrets, infrastructure and pipeline misconfigurations, enriches known vulnerable packages with CVE metadata, and integrates optional Trivy/Semgrep scanners.
