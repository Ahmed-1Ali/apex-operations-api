# Apex Operations API — Junior DevOps Assessment

Small local DevOps demonstration: FastAPI, Docker, Compose, GitHub Actions CI, tests, health/readiness, Prometheus metrics, failure investigation and rollback instructions.

> **Evidence honesty:** these files are a project scaffold. Do not claim CI, deployment, tests or rollback succeeded until you run them and capture your own output/screenshots.

## Architecture
```mermaid
flowchart LR
  Dev[Commit / Pull Request] --> CI[GitHub Actions]
  CI --> L[Lint] --> T[Pytest] --> B[Docker build] --> S[Dependency audit]
  User[Local user] --> Compose[Docker Compose] --> API[FastAPI non-root container]
  API --> H[/health and /ready]
  API --> M[/metrics]
  API --> O[/api/v1/operations]
  API --> Logs[Container logs]
```

## Quick start
Requirements: Docker Desktop/Engine with Compose v2; Python 3.12+ for local tests.
```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
curl -fsS http://127.0.0.1:8000/api/v1/operations
curl -fsS http://127.0.0.1:8000/metrics
```
OpenAPI docs: http://127.0.0.1:8000/docs. Stop with `docker compose down`.

## Test and lint
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ruff check app tests
pytest -q
```
There are nine automated checks. The intentional CI-gate check passes normally but can be made to fail on demand:
```bash
# Expected to exit non-zero; this is intentional
./scripts/test-intentional-failure.sh
```
PowerShell alternative:
```powershell
$env:DEMO_FORCE_TEST_FAILURE = "1"
pytest -q tests/test_api.py::test_ci_failure_gate_opt_in
Remove-Item Env:DEMO_FORCE_TEST_FAILURE
```
Unset the flag before normal testing. A failed lint/test step blocks the later image build in the CI workflow.

## Release and rollback
```bash
APP_VERSION=1.0.1 docker compose build api
APP_VERSION=1.0.1 docker compose up -d --no-build api
curl -fsS http://127.0.0.1:8000/
./scripts/rollback.sh 1.0.0
curl -fsS http://127.0.0.1:8000/
```
Rollback only uses an already-built local tag. For real releases use immutable commit-SHA tags and a registry.

## Observability and incident exercise
- Logs: `docker compose logs --since=10m api`
- Health: `docker compose ps`
- Metrics: `curl -fsS http://127.0.0.1:8000/metrics`
- Inject demo failure: `curl -i http://127.0.0.1:8000/api/v1/debug/failure` (intentional HTTP 500), then inspect logs and practice rollback.

Proposed alerts (not deployed): service unavailable for 1 minute; HTTP 5xx rate above 5% for 5 minutes; p95 latency above 500 ms for 5 minutes; container unhealthy for two checks.

## Security
Non-root runtime; read-only root filesystem; dropped Linux capabilities; no-new-privileges; host port bound to loopback. No credentials are needed. `.env` is gitignored. For real environments use a secret manager, least-privilege identities, dependency audits and image scanning (Trivy/Grype). Synthetic data only; no production access or paid cloud resources.

## File map
`app/main.py`, `Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml`, `tests/test_api.py`, `scripts/rollback.sh`, `scripts/test-intentional-failure.sh`, `docs/RUNBOOK.md`, `docs/DECISION-MEMO.md`.

## AI-use disclosure — verify and retain
AI assistance was used to draft the initial application, container configuration, CI workflow, tests, scripts, README, runbook and decision memo. I will review the implementation, personally execute the tests/deployment/failure/rollback exercises, and submit evidence of actual results. Update this statement to match the assistance actually used.
