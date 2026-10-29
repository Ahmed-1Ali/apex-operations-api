
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "apex-operations-api"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_list_operations(client):
    response = client.get("/api/v1/operations")
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_known_operation(client):
    response = client.get("/api/v1/operations/op-001")
    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"


def test_unknown_operation_404(client):
    response = client.get("/api/v1/operations/nope")
    assert response.status_code == 404
    assert response.json()["detail"] == "operation_not_found"


def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "apex_http_requests_total" in response.text


def test_demo_failure(client):
    response = client.get("/api/v1/debug/failure")
    assert response.status_code == 500
    assert response.json()["detail"] == "intentional_demo_failure"


def test_ci_failure_gate_opt_in():
    if os.getenv("DEMO_FORCE_TEST_FAILURE") == "1":
        pytest.fail("intentional failure: CI must block release")
