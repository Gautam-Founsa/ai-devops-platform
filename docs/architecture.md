# Architecture

The platform starts as a modular monorepo with a FastAPI API gateway and a Next.js operator console. Phase 1 keeps the deployable path small while preserving service boundaries for later extraction.

## Runtime Components

- `frontend`: Next.js 15 dashboard, chat, and metrics UI.
- `backend`: FastAPI API gateway with JWT auth, conversation persistence, synthetic metrics query scaffolding, and Prometheus instrumentation.
- `postgres`: System of record for organizations, users, conversations, incidents, telemetry snapshots, recommendations, audit logs, and runbooks.
- `redis`: Cache and queue foundation for background workers in later phases.
- `prometheus`: Scrapes backend `/metrics`.

## Phase Boundaries

The `services/` and `agents/` directories are intentionally present in Phase 1. They define the future ownership model for log analysis, incidents, Kubernetes, Terraform, CI/CD, security, cost, and multi-agent orchestration.

