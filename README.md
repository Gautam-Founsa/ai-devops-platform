# AI DevOps Platform

Production-grade monorepo scaffold for an AI-powered infrastructure copilot.

## Phase 1

- FastAPI backend with JWT auth, async SQLAlchemy, PostgreSQL, Redis config, AI chat endpoint, health checks, and Prometheus metrics.
- Next.js 15 frontend with dashboard shell, login, AI chat, metrics explorer, Tailwind CSS, Recharts, Framer-ready structure, and shadcn-style primitives.
- Docker Compose for backend, frontend, PostgreSQL, Redis, and Prometheus.
- Monorepo boundaries for future services, agents, infrastructure, monitoring, tests, and docs.

## Run Locally

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/api/docs
- Backend metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090

Register a user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"organization_name":"Acme Ops","email":"admin@example.com","full_name":"Admin User","password":"change-me-123"}'
```

Use the returned bearer token in `/chat` and `/metrics`.

## Monorepo Layout

```text
backend/          FastAPI API gateway and Phase 1 backend services
frontend/         Next.js 15 application shell
services/         Future bounded backend services
agents/           Future AI agents
infrastructure/   Docker, Kubernetes, Helm, and Terraform assets
monitoring/       Prometheus and future Grafana/Loki/OpenTelemetry assets
docs/             Architecture and API notes
tests/            Cross-service integration and E2E tests
scripts/          Developer and operations scripts
```

