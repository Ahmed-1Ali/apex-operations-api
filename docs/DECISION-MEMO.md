# Decision Memo

## Assumptions
The goal is a small reproducible local API. It uses synthetic in-memory data, no customer information, external services, cloud deployment or paid resources. A database is omitted because the demo is read-only and static; add one if persistence becomes a real requirement.

## Decisions and trade-offs
FastAPI provides a minimal API and OpenAPI docs. The multi-stage image keeps build tooling out of the runtime; the process runs non-root. Compose enables read-only filesystem, dropped capabilities, no-new-privileges and loopback binding. GitHub Actions performs lint, tests, image build and dependency audit; failed earlier steps block later steps. Version tags and a rollback script demonstrate the intended workflow, while real releases should use immutable commit-SHA tags in a registry.

Prometheus metrics are exposed at `/metrics`; logs include structured key/value fields. Production improvements would include a dedicated JSON logger, centralized log aggregation, dashboards, alert manager, image scanning, SBOM/signing, staging smoke tests and protected deployment approvals.

## Limitations
The intentional 500 endpoint is for assessment only and must be removed/gated before production. No actual alert backend is provisioned; proposed alerts are API unavailable for 1 minute, 5xx rate above 5% for 5 minutes, p95 latency above 500 ms for 5 minutes, and unhealthy container for two checks. Review dependency audit results instead of assuming they are clean.
