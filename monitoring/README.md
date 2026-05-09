# Monitoring

Phase 1 exposes FastAPI process and request metrics at `/metrics` and scrapes them with Prometheus.

Future phases can add Grafana dashboards, Loki log ingestion, and OpenTelemetry collectors here.

Phase 2 adds ChromaDB for semantic log retrieval. Prometheus continues to scrape backend API metrics.
