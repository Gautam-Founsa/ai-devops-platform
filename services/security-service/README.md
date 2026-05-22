# Security Service

Phase 6 functionality is implemented in the FastAPI gateway under `backend/app/services/security.py`. The default backend Docker image installs Trivy and Semgrep CLIs for native scanner integration.

Future extraction can add repository connectors, SARIF upload, richer CVE feeds, policy-as-code, Trivy server mode, and Semgrep managed rule packs.
