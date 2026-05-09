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
