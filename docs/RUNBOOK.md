# Operations Runbook

## Deploy
1. Install Docker Desktop/Engine and Compose v2.
2. Optional: copy `.env.example` to `.env`.
3. Run `docker compose up --build -d`.
4. Check `/health`, `/ready`, `/api/v1/operations` at `http://127.0.0.1:8000`.
5. Inspect with `docker compose ps` and `docker compose logs --tail=100 api`.

## Release and rollback
Build a new version with `APP_VERSION=1.0.1 docker compose build api`, then deploy it with `APP_VERSION=1.0.1 docker compose up -d --no-build api`. Roll back to a previously built image using `./scripts/rollback.sh 1.0.0`. Verify health endpoints and API output. Rollback deliberately does not build or pull images; the known-good tag must already exist.

## Incident: HTTP 500
Reproduce using `curl -i http://127.0.0.1:8000/api/v1/debug/failure`, inspect `docker compose logs --since=10m api`, inspect health with `docker compose ps`, correlate route/status in logs, then roll back if related to a release and recheck health. Record timeline, impact, root cause and follow-up. The debug failure endpoint is assessment-only and must be removed or gated before production.

## Troubleshooting
- Port occupied: set `API_PORT=8001` in `.env` and recreate the service.
- Container exits: inspect `docker compose logs api`.
- Health fails: check `/health`, container status and startup logs.
- CI fails: reproduce using `pip install -r requirements.txt`, `ruff check app tests`, `pytest -q`, and `docker build -t apex-operations-api:local .`.
- Missing rollback image: build or pull the known-good tag before rollback; never build an unknown candidate as a rollback.

## Security
Run non-root; use read-only root filesystem, drop capabilities, no-new-privileges and loopback-only port binding. No secrets are required; `.env` is gitignored. In real systems use CI secret stores/cloud secret managers and least-privilege IAM. Audit dependencies and scan images (e.g. Trivy/Grype) before production.
