You are a world-class Staff Site Reliability Engineer (SRE), DevOps Architect, MLOps Engineer, and AI Systems Engineer.

Your task is to build a production-grade AI DevOps & Infrastructure Engineer platform.

This platform acts as an autonomous AI infrastructure assistant that can:
- Monitor servers and Kubernetes clusters
- Analyze logs and metrics
- Detect anomalies and outages
- Explain incidents in plain English
- Recommend fixes
- Generate Infrastructure as Code
- Optimize CI/CD pipelines
- Predict failures
- Assist with deployments and rollbacks
- Chat with infrastructure using natural language

====================================================
PRODUCT VISION
====================================================
Build an AI-powered infrastructure copilot similar to combining:
- Datadog
- Grafana
- Prometheus
- Splunk
- Kubernetes Dashboard
- GitHub Actions
- ChatGPT

The system should allow users to ask:
- "Why is my API latency high?"
- "Summarize the last deployment incident."
- "Generate a Terraform file for AWS ECS."
- "Which pods are crashing most often?"
- "What caused the CPU spike at 3 PM?"
- "Suggest optimizations for this Dockerfile."

====================================================
TECH STACK
====================================================
Frontend:
- Next.js 15
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- Framer Motion

Backend:
- FastAPI
- Python 3.12+
- WebSockets
- AsyncIO

AI Layer:
- Ollama
- Qwen3 / Llama 3 / DeepSeek
- LangGraph
- LlamaIndex

Databases:
- PostgreSQL
- Redis
- ChromaDB

Infrastructure:
- Docker
- Docker Compose
- Kubernetes
- Helm

Observability:
- Prometheus
- Grafana
- Loki
- OpenTelemetry

CI/CD:
- GitHub Actions

Cloud Integrations:
- AWS
- GCP
- Azure
- DigitalOcean

====================================================
CORE MODULES
====================================================
1. AI Chat Copilot
2. Metrics Explorer
3. Log Intelligence
4. Incident Analyzer
5. Deployment Monitor
6. Kubernetes Dashboard
7. Terraform Generator
8. Docker Optimizer
9. CI/CD Analyzer
10. Security Scanner
11. Cost Optimization Advisor
12. Root Cause Analysis Engine
13. Alert Correlation Engine
14. Runbook Generator
15. Audit Trail

====================================================
KEY FEATURES
====================================================
AI Chat Copilot:
- Natural language chat with infrastructure
- Streaming responses
- Context-aware conversations
- Source citations

Metrics Analysis:
- CPU, memory, disk, network
- Custom PromQL queries
- Correlation across services

Log Intelligence:
- Semantic log search
- Error clustering
- AI summaries
- Pattern detection

Incident Analyzer:
- Timeline reconstruction
- Root cause hypotheses
- Impact analysis
- Postmortem generation

Deployment Monitor:
- Compare deployments
- Detect regressions
- Rollback suggestions

Kubernetes Support:
- Pod status
- CrashLoopBackOff analysis
- Resource recommendations
- YAML generation

Terraform Generator:
- Natural language to IaC
- Validation
- Security best practices

Dockerfile Optimizer:
- Layer reduction
- Security hardening
- Size optimization

CI/CD Analyzer:
- Parse GitHub Actions
- Detect inefficiencies
- Suggest caching and parallelization

Security Scanner:
- Misconfiguration detection
- Secrets scanning
- CVE enrichment

Cost Advisor:
- Rightsizing recommendations
- Idle resource detection

====================================================
AI AGENTS
====================================================
1. Metrics Agent
2. Logs Agent
3. Kubernetes Agent
4. CI/CD Agent
5. Terraform Agent
6. Security Agent
7. Cost Agent
8. Incident Agent
9. Research Agent
10. Report Agent

====================================================
AGENT WORKFLOW EXAMPLE
====================================================
User: "Investigate why checkout service latency increased after deployment."

1. Incident Agent identifies the timeframe.
2. Deployment Agent fetches deployment metadata.
3. Metrics Agent analyzes latency and resource changes.
4. Logs Agent clusters new errors.
5. Kubernetes Agent checks pod health.
6. Security Agent checks policy violations.
7. Report Agent generates RCA summary.

====================================================
FRONTEND PAGES
====================================================
- /dashboard
- /chat
- /incidents
- /metrics
- /logs
- /deployments
- /kubernetes
- /terraform
- /cicd
- /security
- /cost
- /settings

====================================================
UI COMPONENTS
====================================================
- AI chat panel
- Incident timeline
- Metrics charts
- Log table
- YAML editor
- Diff viewer
- Deployment comparison
- RCA report viewer
- Alert cards
- Resource topology graph

====================================================
BACKEND SERVICES
====================================================
- api-gateway
- auth-service
- ai-orchestrator
- metrics-service
- logs-service
- incident-service
- deployment-service
- kubernetes-service
- terraform-service
- cicd-service
- security-service
- cost-service
- notification-service

====================================================
DATABASE SCHEMA
====================================================
Tables:
- users
- organizations
- clusters
- services
- incidents
- alerts
- deployments
- conversations
- messages
- metrics_snapshots
- logs_embeddings
- recommendations
- audit_logs
- runbooks

====================================================
API ENDPOINTS
====================================================
POST   /api/chat
GET    /api/incidents
POST   /api/incidents/analyze
GET    /api/metrics/query
POST   /api/logs/search
POST   /api/terraform/generate
POST   /api/docker/optimize
POST   /api/cicd/analyze
POST   /api/k8s/explain
POST   /api/security/scan
GET    /api/cost/recommendations

====================================================
AUTHENTICATION & SECURITY
====================================================
- JWT authentication
- OAuth (GitHub, Google)
- RBAC
- Multi-tenant isolation
- API rate limiting
- Secrets encryption
- Audit logging
- SSO-ready architecture

====================================================
OBSERVABILITY
====================================================
- Structured logging
- OpenTelemetry tracing
- Prometheus metrics
- Error monitoring
- Health checks

====================================================
TESTING
====================================================
Unit Tests:
- pytest
- Vitest

Integration Tests:
- API tests
- database tests

E2E Tests:
- Playwright

Load Tests:
- Locust

====================================================
CI/CD PIPELINE
====================================================
- lint
- type checking
- unit tests
- integration tests
- build Docker images
- security scanning
- deploy to staging
- smoke tests
- production deployment

====================================================
MONITORING DASHBOARDS
====================================================
- System health overview
- Incident trends
- Deployment success rate
- Error budget burn
- Cost breakdown
- Security findings

====================================================
ALERTING
====================================================
Integrations:
- Slack
- Email
- Discord
- PagerDuty

====================================================
PRODUCTION REQUIREMENTS
====================================================
- Multi-tenant SaaS architecture
- Horizontal scaling
- Async background workers
- Redis caching
- Queue-based processing
- Graceful retries
- Circuit breakers
- Idempotent jobs
- Database migrations
- Backups
- Disaster recovery

====================================================
PERFORMANCE TARGETS
====================================================
- API response < 300ms (non-AI endpoints)
- Chat first token < 2s local inference
- Dashboard load < 2s
- Support 1,000+ incidents
- Handle millions of log lines

====================================================
PROJECT STRUCTURE
====================================================
ai-devops-platform/
├── frontend/
├── backend/
├── services/
│   ├── ai-orchestrator/
│   ├── metrics-service/
│   ├── logs-service/
│   ├── incident-service/
│   ├── terraform-service/
│   ├── cicd-service/
│   ├── security-service/
│   └── cost-service/
├── agents/
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── helm/
│   └── terraform/
├── monitoring/
├── tests/
├── docs/
└── scripts/

====================================================
IMPLEMENTATION ROADMAP
====================================================
Phase 1:
- Authentication
- Dashboard shell
- AI chat
- Metrics integration

Phase 2:
- Log analysis
- Incident detection

Phase 3:
- Kubernetes analysis
- Deployment monitoring

Phase 4:
- Terraform generation
- CI/CD analyzer

Phase 5:
- Security and cost modules

Phase 6:
- Multi-agent orchestration

Phase 7:
- Monitoring, testing, hardening

Phase 8:
- SaaS multi-tenancy

====================================================
DELIVERABLES
====================================================
Generate:
1. Full folder structure
2. Production-ready source code
3. Docker Compose setup
4. Kubernetes manifests
5. Helm charts
6. Database schema
7. API docs
8. Tests
9. CI/CD workflows
10. README and architecture docs

Start by generating the complete architecture and Phase 1 implementation.