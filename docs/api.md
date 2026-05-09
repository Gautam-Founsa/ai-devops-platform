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
