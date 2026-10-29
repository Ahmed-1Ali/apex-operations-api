import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger("apex_api")
REQUESTS = Counter("apex_http_requests_total", "HTTP requests handled", ["method", "path", "status"])
READY = Gauge("apex_app_ready", "Whether the application is ready")


@asynccontextmanager
async def lifespan(app):
    READY.set(1)
    logger.info("application_started")
    yield
    READY.set(0)
    logger.info("application_stopped")


app = FastAPI(title="Apex Operations API", version=os.getenv("APP_VERSION", "1.0.0"), lifespan=lifespan)


@app.middleware("http")
async def request_log(request: Request, call_next):
    response = await call_next(request)
    REQUESTS.labels(request.method, request.url.path, str(response.status_code)).inc()
    logger.info("request_complete method=%s path=%s status=%s", request.method, request.url.path, response.status_code)
    return response


@app.get("/")
def root():
    return {"service": "apex-operations-api", "version": app.version, "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def readiness():
    return {"status": "ready" if READY._value.get() == 1 else "not_ready"}


OPERATIONS = {
    "op-001": {"id": "op-001", "name": "daily-reconciliation", "status": "succeeded"},
    "op-002": {"id": "op-002", "name": "inventory-sync", "status": "running"},
}


@app.get("/api/v1/operations")
def list_operations():
    return {"items": list(OPERATIONS.values()), "count": len(OPERATIONS)}


@app.get("/api/v1/operations/{operation_id}")
def get_operation(operation_id: str):
    if operation_id not in OPERATIONS:
        raise HTTPException(status_code=404, detail="operation_not_found")
    return OPERATIONS[operation_id]


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/debug/failure")
def intentional_failure():
    raise HTTPException(status_code=500, detail="intentional_demo_failure")
