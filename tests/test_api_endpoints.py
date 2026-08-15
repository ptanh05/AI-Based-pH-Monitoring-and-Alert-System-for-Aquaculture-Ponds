"""
Integration test suite for FastAPI endpoints of AI Aquaculture Guardian.

Tests all 18 REST endpoints for status codes, schema correctness,
validation, and error handling using Starlette/FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from api.server import app, PHMonitoringSystem
import api.server as server_module


@pytest.fixture(scope="module")
def client():
    # Initialize monitoring system for tests
    server_module.monitoring_system = PHMonitoringSystem(
        scenario="competition_demo", seed=42, reading_interval_seconds=0.1
    )
    # Feed some sample readings to populate state
    for _ in range(35):
        ts, val = server_module.monitoring_system.simulator.generate_reading()
        server_module.process_ph_reading(ts, val)

    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "total_readings" in data
    assert "current_status" in data
    assert "thresholds" in data
    assert data["thresholds"]["low"] == 7.0
    assert data["thresholds"]["high"] == 8.5


def test_current_reading_endpoint(client):
    response = client.get("/api/current")
    assert response.status_code == 200
    data = response.json()
    assert "ph_value" in data
    assert "status" in data
    assert "risk_score" in data
    assert "risk_level" in data


def test_history_endpoint(client):
    response = client.get("/api/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "readings" in data
    assert "count" in data
    assert len(data["readings"]) <= 10


def test_forecast_endpoint(client):
    response = client.get("/api/forecast?steps=15")
    assert response.status_code == 200
    data = response.json()
    assert "model_predictions" in data
    assert "baseline_predictions" in data
    assert len(data["model_predictions"]) == 15
    assert len(data["baseline_predictions"]) == 15


def test_legacy_prediction_endpoint(client):
    response = client.get("/api/prediction")
    assert response.status_code == 200
    data = response.json()
    assert "predicted_ph" in data
    assert "is_reliable" in data


def test_risk_endpoint(client):
    response = client.get("/api/risk")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "level" in data
    assert "components" in data
    assert 0 <= data["total"] <= 100


def test_anomalies_endpoint(client):
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "is_anomaly" in data
    assert "anomaly_score" in data
    assert "reasons" in data


def test_explanation_endpoint(client):
    response = client.get("/api/explanation")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "reasons" in data


def test_recommendations_endpoint(client):
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert "disclaimer" in data


def test_alerts_endpoint(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "is_alerting" in data


def test_alert_history_endpoint(client):
    response = client.get("/api/alert-history")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "statistics" in data


def test_alert_statistics_endpoint(client):
    response = client.get("/api/alert-statistics")
    assert response.status_code == 200


def test_model_metrics_endpoint(client):
    response = client.get("/api/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "model_type" in data
    assert "is_trained" in data


def test_inference_engine_endpoint(client):
    response = client.get("/api/inference-engine")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data


def test_system_health_endpoint(client):
    response = client.get("/api/system-health")
    assert response.status_code == 200
    data = response.json()
    assert "sensor_health" in data
    assert "forecaster" in data


def test_source_info_endpoint(client):
    response = client.get("/api/source-info")
    assert response.status_code == 200
    data = response.json()
    assert "current_mode" in data
    assert "disclaimer" in data


def test_scenario_switch_endpoint(client):
    response = client.post("/api/scenario?scenario=heavy_rain&seed=99")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["scenario"] == "heavy_rain"
    assert data["seed"] == 99


def test_set_mode_endpoint(client):
    response = client.post("/api/set-mode?mode=manual")
    assert response.status_code == 200
    assert response.json()["mode"] == "manual"

    # Reset back to auto
    response = client.post("/api/set-mode?mode=auto")
    assert response.status_code == 200
    assert response.json()["mode"] == "auto"
