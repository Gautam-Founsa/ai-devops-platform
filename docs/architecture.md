# Architecture

The platform starts as a modular monorepo with a FastAPI API gateway and a Next.js operator console. Phase 1 keeps the deployable path small while preserving service boundaries for later extraction.

## Runtime Components

- `frontend`: Next.js 15 dashboard, chat, and metrics UI.
- `backend`: FastAPI API gateway with JWT auth, conversation persistence, synthetic metrics query scaffolding, and Prometheus instrumentation.
- `postgres`: System of record for organizations, users, conversations, incidents, telemetry snapshots, recommendations, audit logs, and runbooks.
- `redis`: Cache and queue foundation for background workers in later phases.
- `chromadb`: Vector index for semantic log intelligence and incident evidence retrieval.
- `prometheus`: Scrapes backend `/metrics`.

## Kubernetes Intelligence

Phase 3 adds `/api/v1/k8s/*` endpoints for cluster overview, pod exploration, CrashLoopBackOff analysis, resource recommendations, YAML explanation, and manifest generation. The service currently uses deterministic demo telemetry so the UI and API work without local kubeconfig access; the boundary is ready for a Kubernetes client adapter.

## Terraform Generation

Phase 4 adds `/api/v1/terraform/*` endpoints for natural language to Terraform generation, AWS ECS/RDS/ALB templates, static validation, and security best-practice guidance. Generation is deterministic and reviewable so users can inspect every produced `.tf` file before applying it.

## CI/CD Intelligence

Phase 5 adds `/api/v1/cicd/*` endpoints for GitHub Actions parsing, workflow scoring, inefficiency detection, optimization suggestions, and safer generated workflow YAML. The analyzer is static and deterministic so it can run before any repository connector is added.

## Security Scanning

Phase 6 adds `/api/v1/security/*` endpoints for secrets detection, misconfiguration analysis, local CVE enrichment, persisted findings, and Trivy/Semgrep integration hooks. The backend Docker image installs Trivy and Semgrep for native scans; if they are absent in a custom runtime, the platform falls back to built-in static checks.

## Phase Boundaries

The `services/` and `agents/` directories are intentionally present in Phase 1. They define the future ownership model for log analysis, incidents, Kubernetes, Terraform, CI/CD, security, cost, and multi-agent orchestration.
